# chakoshi MCP Server

  

MCPクライアントアプリケーションと、[chakoshi API](https://chakoshi.ntt.com) を連携するMCP (Model Context Protocol) サーバーです。

Claude Desktop などからchakoshiを利用して日本語テキストのモデレーション(有害性チェック)を実行できます。

  

## chakoshiとは

  

chakoshiとは、NTT Communicationsが提供するLLM向けのガードレールです。詳細は以下をご覧ください。

[chakoshi 製品ページ](https://chakoshi.ntt.com)

[chakoshi 技術詳細](https://www.anlp.jp/proceedings/annual_meeting/2025/pdf_dir/P7-7.pdf)

[chakoshi ドキュメントサイト](https://docs.chakoshi.ntt.com)

  

## リポジトリに含まれるツール

### 本リポジトリの構成

```

chakoshi-mcp-server/

├── main.py # エントリポイント

├── chakoshi_server/

│ ├── __init__.py

│ ├── config.py # 環境変数の管理

│ └── server.py # MCP サーバーの実装部分

├── pyproject.toml # プロジェクト設定

└── .env # 環境変数（要作成）

```

### moderate_text

 
テキストコンテンツの有害性をチェックするツールです。

  

**入力パラメータ:**

-  `text` (string, 必須): チェックしたいテキスト

  

**出力:**

- chakoshi API からのモデレーション結果をJSON形式で返します

  

**使用プロンプト例:**

```

chakoshi を使ってこのテキストをチェックしてください: "問題のあるコンテンツの例"

```

  

## chakoshi API の設定

  
### API キーの取得
1. [chakoshiのプレイグラウンド](https://platform.beta.chakoshi.ntt.com/playground)にアクセスし、画面に従って新規登録フローを進めてください。

2. 新規登録、およびログイン完了後、プレイグラウンドの設定をクリックします。

3. その後、設定画面からAPIキーを新規に発行します。

  

### カテゴリセットの設定
1. プレイグラウンドにアクセスし、「新しいカスタム検知項目の追加」をクリックし、検知項目名とカスタム検知項目の定義を入力します。 

2. 別名で保存を選択し、新しくカスタム検知項目セットを保存します。

3. 保存後、「選択中の検知項目セットIDをコピー」の項目からカテゴリセットIDをコピーします。


## 必要要件

  

- Python 3.10 以上

- chakoshi のユーザ登録、および、APIキー

- MCPクライアントアプリケーション (Claude Desktopなど)

  

## インストール

  

### 1. リポジトリのクローン

  

```bash

git clone https://github.com/nttcom/chakoshi-mcp-server.git

cd chakoshi-mcp-server

```

  

### 2. 依存関係のインストール

  

```bash

# uvのインストール
curl -LsSfhttps://astral.sh/uv/install.sh | sh


# PATHの設定
source $HOME/.local/bin/env


# uv を使用する場合（推奨）

uv sync


# pip を使用する場合

pip install -e .

```

  

### 3. 環境変数の設定

  

`.env` ファイルを作成し、以下の環境変数を設定してください：

  

```env

CHAKOSHI_API_KEY=your_chakoshi_api_key

CHAKOSHI_API_URL=https://api.beta.chakoshi.ntt.com/v1/judge/text

CHAKOSHI_MODEL_ID=chakoshi-moderation-241223

CHAKOSHI_CATEGORY_SET_ID=your_category_set_id

CHAKOSHI_TIMEOUT_SEC=5

```

  

**注意**: 実際の APIキーとカテゴリセットID はchakoshiプレイグラウンドの管理画面から取得してください。

  

## 使用方法

### サーバの起動
```
uv run main.py
```



### Claude Desktop との連携

  

Claude Desktop の設定ファイル（`claude_desktop_config.json`）に以下を追加：

  

```json

{

"mcpServers": {

"command": "/PATH_to_uv/uv",
        "args": [
          "--directory",
          "/PATH_to_chakoshi/chakoshi-mcp-server",
          "run",
          "main.py"
        ],
        "env": {
          "CHAKOSHI_API_KEY": "YOUR_CHAKOSHI_API_KEY"
        }

}

}

```

  

その後、Claude Desktop 内で以下のように使用できます：

  

```

chakoshiを使ってこのテキストをチェックしてください：「問題のあるコンテンツの例」

```

  

Claude が自動的に `moderate_text` ツールを使用してモデレーション結果を返します。

  

## API レスポンス例

  

```json


{
  "category1": {
    "score": 0.05,
    "threshold": 0.5,
    "result": "safe"
  },
  "category2": {
    "score": 0.02,
    "threshold": 0.3,
    "result": "safe"
  }
}


```
  

## 注意事項


- chakoshi API は現在ベータ版です。本番環境などでは使用しないでください。

- APIキーは適切に管理し、決して公開しないでください。

- APIキーのレート制限などについては[公式ドキュメント](https://docs.chakoshi.ntt.com)を参照してください。


## ライセンス
MIT
