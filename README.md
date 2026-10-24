# Joy-Con Mouse

Windows向けの、Joy-Conのアナログスティックでカーソルを動かすマウスツールです。ジャイロ・加速度センサーは使用しません。

## 機能
- GUIスライダーでカーソル速度を調整（100〜2000 px/s）
- 独立したホイール速度スライダー（1〜40段/秒、初期値12）
- LRモードでは右スティックの倒し具合に応じてホイール速度が変化し、分数ステップを蓄積して滑らかにスクロール
- 実際の処理間隔を使って移動・スクロール量を計算
- 入力デバイスをキャッシュして処理負荷を低減。詳細な入力ログは既定でオフ
- Lスティックでカーソル移動
- LRモードではRスティック上下でホイールスクロール
- Rのみモードでは右Joy-ConのX/Bでホイール上/下
- Lのみモードでは十字キー↑/↓でホイール上/下
- 指定ボタンで左クリック・右クリック

## 操作割り当て
| 接続状態 | カーソル移動 | 左クリック | 右クリック | ホイール上 | ホイール下 |
|---|---|---|---|---|---|
| Rのみ | Rスティック | A / ZR | Y / R | X | B |
| Lのみ | Lスティック | 十字キー左 / ZL | 十字キー右 / L | 十字キー↑ | 十字キー↓ |
| L + R | Lスティック | L / ZL / A / 十字キー左 | R / ZR / Y / 十字キー右 | Rスティック上 | Rスティック下 |

## セットアップ
Python 3.10 以降を推奨します。

```bash
py -m pip install -r requirements.txt
py joycon_mouse.py
```

Joy-ConをWindowsにBluetoothでペアリングしてから起動してください。起動するとカーソル速度とホイール速度を調整できるウィンドウが開きます。詳細な入力ログは既定でオフです。

## 注意
Joy-Conのボタン番号・軸番号は、WindowsのドライバーやSDL/pygameのバージョンによって異なることがあります。この初期実装は一般的なSDLのボタン順を初期値として使っています。実機での確認と必要に応じたマッピング調整が必要です。複合デバイスではスティック軸を0/1（左）と2/3（右）として扱うため、環境によって軸の割り当て調整が必要な場合があります。依存パッケージにはWindows/新しいPython向けのwheelが利用しやすい `pygame-ce` を使用しています。

このツールはWindows/SDLが公開するゲームコントローラー入力を利用し、Bluetooth HIDの生パケットを直接解析しません。

## 参照資料
- https://github.com/dekuNukem/Nintendo_Switch_Reverse_Engineering/blob/master/bluetooth_hid_notes.md
- https://github.com/dekuNukem/Nintendo_Switch_Reverse_Engineering/blob/master/bluetooth_hid_subcommands_notes.md
