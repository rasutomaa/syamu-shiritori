# Syamuあだ名しりとり

Syamuあだ名リストを使ってしりとりをするPythonプロジェクトです。

## セットアップ

```bash
git clone https://github.com/rasutomaa/syamu-shiritori.git
cd syamu-shiritori
pip install -r requirements.txt
```

`data/Syamuあだ名しりとり.txt` に元のリストが入っていることを確認してください。

```bash
ls data/
# => Syamuあだ名しりとり.txt
```

もしファイルが見つからない場合：

```bash
データファイルが見つかりません: data/Syamuあだ名しりとり.txt
```

と表示されるので、UTF-8で保存したリストを `data/` の中に置いてください。

---

## 使い方

使い方は3つのモードがあります。

### ① 対話モード（実際にしりとりする）

```bash
python shiritori.py play
```

流れ：

1. `最初のあだ名:` と聞かれる → リストのあだ名を1つ入力  
   例：`会いに行ける無職`
2. コンピュータが次のあだ名を返す
3. `次のあだ名:` と聞かれる → 直前の末尾に合うあだ名を入力
4. コンピュータが返せなくなったら、あなたの勝ち
5. やめたいときは空Enter

入力例：

```text
最初のあだ名: 会いに行ける無職
開始: 1 会いに行ける無職

現在: 1 会いに行ける無職 (末尾: く)
次のあだ名: クッキーモンスター
あなた: 2 クッキーモンスター
コンピュータ: 99 タケノコ無職 (末尾: く)
...
```

### ② 自動生成モード（プログラムが全部やる）

```bash
python shiritori.py auto
```

長めのしりとりチェーンを自動で生成して表示します。

試行回数を増やすと、より長いチェーンが見つかりやすくなります：

```bash
python shiritori.py auto --tries 5000
```

### ③ 検証モード（作ったチェーンが正しいか確認）

`chain.txt` に1行1あだ名で書いて検証できます：

```bash
python shiritori.py validate chain.txt
```

成功すると：

```text
OK: 有効なしりとりチェーンです。
```

失敗すると、どの行がおかしいか表示されます。

---

## トラブルシューティング

### `pykakasi` のインストールで失敗する

`requirements.txt` のバージョン指定が古い可能性があります。  
以下に変更してください：

```txt
pykakasi>=2.3.0
```

その後、再度インストール：

```bash
pip install -r requirements.txt
```

### データファイルが見つからない

```bash
ls data/
```

で `Syamuあだ名しりとり.txt` があるか確認してください。  
なければ `data/` ディレクトリを作成し、UTF-8で保存したリストを配置してください。

```bash
mkdir -p data
# data/Syamuあだ名しりとり.txt を置く
```

### 動作確認

```bash
python -c "import pykakasi; print(pykakasi.__version__)"
```

でバージョンが表示されれば正常です。

---

## ライセンス

MIT
