import argparse
import sys
from typing import List, Optional
from textmeld.textmeld import TextMeld

def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="A tool to merge multiple text files into one file"
    )
    parser.add_argument(
        "directory",
        help="Path to the directory to be processed"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to the output file (if not specified, output to stdout)",
        default=None
    )
    parser.add_argument(
        "-e", "--exclude",
        help="File patterns to exclude (can specify multiple)",
        action="append",
        default=None
    )
    parser.add_argument(
        "-m", "--max-chars",
        help="Maximum number of characters in the output",
        type=int,
        default=None
    )
    return parser.parse_args()

def main() -> int:
    """メイン関数"""
    try:
        args = parse_args()
        
        # 除外パターン設定
        exclude_patterns = args.exclude or []
        
        # 出力ファイルが指定されている場合は除外リストに追加
        if args.output:
            # 出力ファイルの絶対パスを取得
            import os
            output_path = os.path.abspath(args.output)
            # 出力ファイル名を除外パターンに追加
            exclude_patterns.append(os.path.basename(output_path))
        
        # TextMeldインスタンスの作成
        meld = TextMeld(exclude_patterns=exclude_patterns, max_chars=args.max_chars)
        
        # ディレクトリの処理
        result = meld.process_directory(args.directory)
        
        # 結果の出力
        if args.output:
            # ファイルに出力
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Result has been output to {args.output}.", file=sys.stderr)
        else:
            # 標準出力に出力
            print(result)
        
        return 0
    
    except KeyboardInterrupt:
        print("\nProcess was interrupted.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())