# Flask TODO App with Docker & Nginx

このプロジェクトは、**Flaskで作ったシンプルなTODOアプリ**を、**DockerでMySQLと連携**させつつ、**Nginxコンテナを使ってサブドメインで公開**する構成になっています。

---

## 構成

- **Flask Webアプリ**  
  - `/app` ディレクトリにFlaskアプリを配置
  - `models.py` にTODOのDBモデル
  - `init_db.py` でDBテーブル作成

- **データベース**  
  - MySQLコンテナで動作
  - `.env` でユーザー名、パスワード、DB名などを管理

- **Nginxプロキシ**  
  - `jwilder/nginx-proxy` と `nginxproxy/acme-companion` を使用
  - Dockerネットワークに入れることで、複数プロジェクトでも共通のリバースプロキシを利用可能
  - Let's EncryptでSSL対応（HTTPS公開）

---

## セットアップ

1. **環境変数設定** (`.env` ファイル)

```env
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=todo_db
DB_HOST=mysql_db

LETSENCRYPT_EMAIL=your_email@example.com
VIRTUAL_HOST=todo_flask.go-pro-world.net
LETSENCRYPT_HOST=todo_flask.go-pro-world.net
```

Docker Composeで起動
```bash
docker compose up -d --build
```

DB初期化
```bash
docker exec -it flask_web python init_db.py
```

ブラウザでアクセス
```bash
https://todo_flask.go-pro-world.net/
```

ポイント
FlaskアプリはMySQLに接続してデータを永続化

Nginxコンテナを共通ネットワークに入れることで、複数のサービスを同じドメインやサブドメインで管理可能

Docker ComposeでアプリとDB、プロキシをまとめて起動・管理可能

ディレクトリ構成
```bash
flask-docker-app/
├─ app.py
├─ models.py
├─ init_db.py
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
└─ .env
```

使い方
/add でタスク追加

/done/<id> でタスク完了

/delete/<id> でタスク削除
