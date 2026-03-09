# chakoshi MCP Server

  

MCPクライアントアプリケーションと、[chakoshi API](https://chakoshi.ntt.com) を連携するMCP (Model Context Protocol) サーバーです。

Claude Desktop などからchakoshiのAPIを利用して、テキストの安全性判定を実行できます。

  

## chakoshiとは

  

chakoshiとは、NTT ドコモビジネスが提供するLLM向けのガードレールです。詳細は以下をご覧ください。

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

 
テキストコンテンツをchakoshiのガードレールでチェックするツールです。

  

**入力パラメータ:**

-  `text` (string, 必須): チェックしたいテキスト（最大2000文字）

  

**出力:**

- chakoshi Guardrails Apply API からのアセスメント結果をJSON形式で返します

  

**使用プロンプト例:**

```

chakoshi を使ってこのテキストをチェックしてください: "問題のあるコンテンツの例"

```

  

## chakoshi API の設定

  
### API キーの取得
1. [chakoshiのプレイグラウンド](https://platform.beta.chakoshi.ntt.com/playground)にアクセスし、画面に従って新規登録フローを進めてください。

2. 新規登録、およびログイン完了後、プレイグラウンドの設定をクリックします。

3. その後、設定画面からAPIキーを新規に発行します。

  

### ガードレールの作成
chakoshiのGuardrails Apply API を利用するためには、ポリシー設定をあらかじめ完了してガードレールIDを発行している必要があります。

ポリシー設定とガードレールIDの発行手順については、[クイックスタート ガードレールの作成](https://docs.chakoshi.ntt.com)を参照してください。


## 必要要件

  

- Python 3.10 以上

- chakoshi のユーザ登録、APIキー、およびガードレールID

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

CHAKOSHI_API_URL=https://api.beta.chakoshi.ntt.com/v1/guardrails/apply

CHAKOSHI_GUARDRAIL_ID=your_guardrail_id

CHAKOSHI_TIMEOUT_SEC=10

```

  

**注意**: 実際の APIキーとガードレールID はchakoshiプレイグラウンドの管理画面から取得してください。

  

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
        ]
}

}

```

  

その後、Claude Desktop 内で以下のように使用できます：

  

```

chakoshiを使ってこのテキストをチェックしてください：「問題のあるコンテンツの例」

```

  

Claude が自動的に `moderate_text` ツールを使用してモデレーション結果を返します。

  

## API レスポンス例

Guardrails Apply API のレスポンスから `assessments` フィールドを抽出して返します。

```json
{
  "guardrails": ["moderation", "keyword_filter"],
  "user_input": "チェック対象のテキスト",
  "guardrails_result": {
    "moderation": {
      "unsafe_flag": false,
      "unsafe_score": 0.05,
      "categories": {
        "violence": {
          "enabled": true,
          "detected": false
        },
        "harassment": {
          "enabled": true,
          "detected": false
        }
      }
    },
    "keyword_filter": {
      "matched": false,
      "matches": [],
      "original_text": "チェック対象のテキスト",
      "masked_input": "チェック対象のテキスト"
    }
  }
}
```
  

## 注意事項


- chakoshi API は現在ベータ版です。本番環境などでは使用しないでください。

- APIキーは適切に管理し、決して公開しないでください。

- APIキーのレート制限などについては[公式ドキュメント](https://docs.chakoshi.ntt.com)を参照してください。


## ライセンス
MIT
