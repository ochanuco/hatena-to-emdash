# hatena-to-emdash

はてなブログの MT 形式エクスポートを EmDash 向けの Markdown に変換するための小さな CLI です。

## できること

- MT 形式の記事を 1 記事ずつ解析
- frontmatter 付き Markdown を生成
- 本文中の画像 URL を抽出
- 画像をローカルへ保存して参照先を書き換え
- 実行レポートを JSON で出力

## 使い方

初期化:

```sh
mise install
mise run init
```

入力ファイルは `./.local/input/*.export.txt` を自動検出します。1件だけ置いてください。

```sh
mise run migrate
```

dry-run:

```sh
mise run migrate:dry-run
```

既定以外のパスを使う場合:

```sh
uv run --python 3.12 python -m hatena_to_emdash.cli migrate --input /path/to/export.txt --output-dir /path/to/output
```

同梱サンプルでの疎通確認:

```sh
mise run migrate:sample
```

テスト:

```sh
mise run test
```

## 出力構成

- `posts/YYYY/MM/slug.md`
- `assets/YYYY/MM/slug/<image files>`
- `migration-report.json`

## 今後の調整候補

- EmDash 固有の frontmatter 項目
- slug 生成ルール
- カテゴリとタグのマッピング
- 外部画像 URL の扱い
