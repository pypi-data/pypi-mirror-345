import anyio
import json
import logging
import argparse # 追加
import sys      # 追加
from mcp import ClientSession
from mcp.shared.exceptions import McpError
from mcp.client.stdio import stdio_client, StdioServerParameters

# ロギング設定 (デフォルトレベルをWARNINGに変更し、main内で再設定)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# TODO: run_client のシグネチャを (args: argparse.Namespace) のように変更する
async def run_client(args: argparse.Namespace):
    """MCPサーバーに接続し、ツールを実行またはリスト表示するクライアント"""

    # MCP定義ファイルの読み込み (エラーはmainでキャッチ)
    with open(args.mcp_def, 'r') as f:
        mcp_def = json.load(f)
    logger.info(f"MCP定義ファイルを読み込みました: {args.mcp_def}")

    mcp_servers = mcp_def.get("mcpServers", {})
    if not mcp_servers:
        # 仕様上、これは設定ファイルエラーとしてmainで処理されるべき
        # ここでは分かりやすいエラーメッセージで例外を発生させる
        raise ValueError("MCP定義ファイルに `mcpServers` 定義が見つかりません。")

    # 最初のサーバー定義を使用
    server_key = next(iter(mcp_servers))
    server_info_def = mcp_servers[server_key]
    command = server_info_def.get("command")
    args_list = server_info_def.get("args", [])

    if not command:
        raise ValueError(f"サーバー '{server_key}' の `command` が定義されていません。")

    server_params = StdioServerParameters(command=command, args=args_list)
    logger.info(f"サーバープロセス起動試行: {command} {' '.join(args_list)}")

    # stdio_client と ClientSession のコンテキスト内で処理
    # エラーは main 側でキャッチするため、ここでは raise する
    async with stdio_client(server_params) as (read, write):
        logger.info("stdio接続成功。")
        async with ClientSession(read, write) as session:
            logger.info("ClientSession作成完了。初期化開始...")
            server_info = await session.initialize()
            logger.info("ClientSession初期化完了！")
            logger.debug(f"サーバー情報: {server_info}") # verbose時のみ

            # --- モード分岐 ---
            if args.tool_def:
                # モード1: ツール実行
                logger.info(f"ツール実行モード開始 (定義ファイル: {args.tool_def})")

                # ツール定義ファイルの読み込み (エラーはmainでキャッチ)
                with open(args.tool_def, 'r') as f:
                    tool_call_def = json.load(f)
                logger.info(f"ツール定義ファイルを読み込みました: {args.tool_def}")

                # 形式チェック
                tool_name = tool_call_def.get("name")
                tool_args = tool_call_def.get("args")

                if not isinstance(tool_name, str) or not tool_name:
                    raise ValueError("ツール定義ファイルに有効な `name` (文字列) がありません。")
                if not isinstance(tool_args, dict):
                     # args が省略された場合 (引数なしツール) は空のdictを許容する
                     if tool_args is None:
                         tool_args = {}
                     else:
                         raise ValueError("ツール定義ファイルの `args` はオブジェクト形式（辞書）である必要があります。")


                logger.info(f"ツール '{tool_name}' を引数 {tool_args} で実行します...")
                try:
                    # session.call_tool からは MCPライブラリがラップしたオブジェクトが返る
                    response_obj = await session.call_tool(tool_name, tool_args)
                    logger.info(f"ツール '{tool_name}' の実行完了。")
                    logger.debug(f"ツール実行レスポンスオブジェクト: {response_obj}") # verbose時のみ

                    # レスポンスオブジェクトに 'isError' と 'content' 属性があるかチェック
                    if hasattr(response_obj, 'isError') and hasattr(response_obj, 'content'):
                        # isError が true の場合は、ツール実行エラーとして例外を投げる
                        if getattr(response_obj, "isError", False): # isError がない場合はFalse扱い
                             logger.error(f"ツール '{tool_name}' がエラーを報告しました。", exc_info=args.verbose)
                             # エラー情報をJSONでstderrに出力 (main側で処理)
                             # content の中身がエラー詳細なので、それをそのまま渡す
                             error_details = getattr(response_obj, "content", [])
                             # McpError の details に含めるために、content を文字列化または適切な形式に変換する必要があるかも
                             # ここではシンプルに、エラーメッセージとして content 全体を文字列化して渡す
                             error_message = f"Tool '{tool_name}' reported an error. Details: {json.dumps(error_details, ensure_ascii=False, default=str)}"
                             raise McpError(error_message, details=error_details) # main側でキャッチ
                        else:
                            # isError が false の場合は、成功結果として content をJSON形式で標準出力へ
                            logger.info(f"ツール '{tool_name}' の実行成功！")
                            try:
                                # content 属性はリストまたは単一のオブジェクトの可能性がある
                                # JSONシリアライズできないオブジェクトは文字列に変換して出力
                                print(json.dumps(response_obj.content, indent=2, ensure_ascii=False, default=str))
                            except TypeError as e:
                                 logger.error(f"ツール結果コンテンツのJSONシリアライズに失敗: {e}", exc_info=args.verbose)
                                 # シリアライズできない場合はそのまま表示試行 (ベストエフォート)
                                 print(response_obj.content)
                                 # シリアライズエラーは設定エラーとして終了コード2にするため、ValueErrorを投げる
                                 raise ValueError(f"ツール結果コンテンツのJSONシリアライズに失敗: {e}")

                    # レスポンスオブジェクトに 'error' 属性があるかチェック (JSON-RPCレベルのエラー)
                    elif hasattr(response_obj, 'error'):
                        rpc_error = response_obj.error
                        logger.error(f"JSON-RPCエラーが発生しました: {rpc_error}", exc_info=args.verbose)
                        # JSON-RPCエラーはMcpErrorとしてラップしてmain側で処理
                        # rpc_error オブジェクトの属性にアクセス
                        raise McpError(f"JSON-RPC Error: {getattr(rpc_error, 'message', 'Unknown RPC error')}", code=getattr(rpc_error, 'code', None), details=rpc_error)

                    else:
                        # 予期しないレスポンスオブジェクトの形式
                        logger.error(f"予期しないレスポンスオブジェクトの形式: {response_obj}", exc_info=args.verbose)
                        raise ValueError(f"予期しないレスポンスオブジェクトの形式: {response_obj}") # main側で処理

                except McpError as e:
                    logger.error(f"ツール '{tool_name}' の実行中にMCPエラーが発生しました。", exc_info=args.verbose)
                    raise # main側で処理するため再送出
                except Exception as e:
                    logger.error(f"ツール '{tool_name}' の実行中に予期せぬエラーが発生しました。", exc_info=args.verbose)
                    raise # main側で処理するため再送出

            else:
                # モード2: ツールリスト表示
                logger.info("ツールリスト表示モード開始")
                try:
                    logger.info("session.list_tools() 呼び出し前")
                    list_tools_result = await session.list_tools()
                    logger.info("session.list_tools() 呼び出し成功")

                    tool_info_list = []
                    if hasattr(list_tools_result, 'tools') and isinstance(list_tools_result.tools, list):
                        tool_info_list = list_tools_result.tools
                        logger.info(f"{len(tool_info_list)} 個のツールが見つかりました。")
                    else:
                        logger.warning("list_tools() の結果からツールリストを取得できませんでした。")
                        logger.debug(f"list_tools() 結果: {list_tools_result}")
                        # ツールリストが取得できなくてもエラーとはせず、空リストを出力する

                    # 仕様書通りの形式に整形してJSONで標準出力へ
                    output_list = []
                    for tool in tool_info_list:
                        # ToolInfo オブジェクトに必要な属性があるか確認しながら整形
                        tool_data = {
                            "name": getattr(tool, 'name', 'N/A'),
                            "description": getattr(tool, 'description', 'N/A'),
                            "inputSchema": getattr(tool, 'inputSchema', None),
                            "outputSchema": getattr(tool, 'outputSchema', None) # 存在しない場合もある
                        }
                        # スキーマがNoneでないか、または空のオブジェクトでないことを確認
                        if not tool_data["inputSchema"]: tool_data["inputSchema"] = {}
                        if not tool_data["outputSchema"]: tool_data["outputSchema"] = {} # nullではなく空オブジェクトに

                        output_list.append(tool_data)

                    print(json.dumps(output_list, indent=2, ensure_ascii=False))

                except McpError as e:
                    logger.error("ツールリストの取得中にMCPエラー発生", exc_info=args.verbose)
                    raise # main側で処理するため再送出
                except Exception as e:
                    logger.error("ツールリストの取得中に予期せぬエラー発生", exc_info=args.verbose)
                    raise # main側で処理するため再送出

    logger.info("stdio_client コンテキストを抜けました。")
    # 正常終了時は run_client からは何も返さず、main側でexit_code=0となる

def main():
    """MCP Client CLIのエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="MCP Client CLI to interact with MCP Servers.",
        epilog="Example: uv python test_mcp_connection.py --mcp-def server.json --tool-def tool.json -v"
    )
    parser.add_argument(
        "--mcp-def",
        required=True,
        help="Path to the MCP server definition JSON file.",
        metavar="FILE_PATH"
    )
    parser.add_argument(
        "--tool-def",
        required=False, # オプションに変更
        default=None,   # デフォルトはNone
        help="Path to the JSON file defining the tool name and arguments. "
             "Format: {'name': 'tool_name', 'args': {...}}",
        metavar="FILE_PATH"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging (INFO level)."
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
         # argparse が --help などで終了した場合や引数エラーの場合
         # argparse は自動でメッセージを stderr に出力し、終了コードを設定する
         sys.exit(e.code) # argparse が設定した終了コードで終了

    # verboseフラグに基づいてロギングレベルを設定
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
        logger.info("Verbose logging enabled.")
        logger.debug(f"Parsed arguments: {args}") # デバッグ用に引数表示
    else:
        # デフォルトはWARNINGレベル (basicConfigで設定済み)
        logging.getLogger().setLevel(logging.WARNING)


    # --- ここから実行ロジック ---
    mcp_definition_file = args.mcp_def
    tool_definition_file = args.tool_def

    exit_code = 0 # デフォルトは正常終了
    try:
        logger.info(f"Starting client with MCP definition: {mcp_definition_file}")
        if tool_definition_file:
            logger.info(f"Mode: Tool Execution (using {tool_definition_file})")
        else:
            logger.info("Mode: List Tools")

        # run_client に args オブジェクトを渡すように変更
        anyio.run(run_client, args)

        logger.info("Client finished successfully.") # ここに到達すれば正常終了

    except FileNotFoundError as e:
         logger.error(f"Configuration file not found: {e}", exc_info=args.verbose)
         # 仕様書通り、人間が読みやすい形式でstderrに出力
         print(f"Error: File not found - {e}", file=sys.stderr)
         exit_code = 2 # 引数/設定エラー
    except (json.JSONDecodeError, ValueError) as e: # ValueErrorも設定ファイル関連のエラーとして扱う
         logger.error(f"Invalid configuration file format: {e}", exc_info=args.verbose)
         # 仕様書通り、人間が読みやすい形式でstderrに出力
         print(f"Error: Invalid configuration file format - {e}", file=sys.stderr)
         exit_code = 2 # 引数/設定エラー
    except McpError as e: # MCP関連のエラー (接続、ツール実行、リスト取得など)
         logger.error(f"MCP Error occurred: {e}", exc_info=args.verbose) # ログは詳細に
         # 仕様に基づきエラー情報をJSONでstderrに出力
         error_output = {
             "error": type(e).__name__, # エラークラス名
             "message": str(e),
             "details": getattr(e, 'details', None) # 詳細があれば含める
         }
         print(json.dumps(error_output, ensure_ascii=False), file=sys.stderr)
         exit_code = 1 # ツール実行/リスト取得エラー
    except Exception as e:
        # その他の予期せぬエラー
        logger.error(f"An unexpected error occurred: {e}", exc_info=args.verbose)
        # 仕様に基づきエラー情報をJSONでstderrに出力 (汎用)
        error_output = {
            "error": type(e).__name__,
            "message": str(e),
            "details": None # 予期せぬエラーでは詳細は不明とする
        }
        print(json.dumps(error_output, ensure_ascii=False), file=sys.stderr)
        exit_code = 1 # ツール実行/リスト取得エラー (またはその他)

    sys.exit(exit_code) # 最終的な終了コードで終了

if __name__ == "__main__":
    main() # main関数を呼び出すように変更