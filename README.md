# Joy-Con Mouse

Windows向けの、Joy-Conのアナログスティックでカーソルを動かすマウスツールです。ジャイロ・加速度センサーは使用しません。

## 機能
- 左右どちらのスティックでもカーソルを移動（左右の入力は合成し、移動量が過大にならないよう制限）
- GUIのスライダーでカーソル速度を調整（100〜2000 px/s）
- 接続されたJoy-Conを名前から検出し、右のみ・左のみ・左右両方のモードを自動選択
- 指定したボタンによる左クリック・右クリック
- 押下エッジでクリックするため、押しっぱなしで連打しない

## クリック割り当て
| 接続状態 | 左クリック | 右クリック |
|---|---|---|
| Rのみ | A / ZR | Y / R |
| Lのみ | 十字キー左 / ZL | 十字キー右 / L |
| L + R | L / ZL / A / 十字キー左 | R / ZR / Y / 十字キー右 |

## セットアップ
Python 3.10 以降を推奨します。

```bash
py -m pip install -r requirements.txt
py joycon_mouse.py
```

Joy-ConをWindowsにBluetoothでペアリングしてから起動してください。起動すると速度調整用のウィンドウが開きます。コンソールには接続デバイスと入力変化も表示されます。

## 注意
Joy-Conのボタン番号・軸番号は、WindowsのドライバーやSDL/pygameのバージョンによって異なることがあります。この初期実装は一般的なSDLのボタン順を初期値として使っています。実機での確認と必要に応じたマッピング調整が必要です。起動ログにはJoy-Con以外も含むSDL検出デバイス名・軸数・ボタン数が表示されます。`Mode=NONE` の場合、そのログを確認してください。複合デバイスではスティック軸を0/1（左）と2/3（右）として扱うため、環境によって軸の割り当て調整が必要な場合があります。依存パッケージにはWindows/新しいPython向けのwheelが利用しやすい `pygame-ce` を使用しています。

このツールはWindows/SDLが公開するゲームコントローラー入力を利用し、Bluetooth HIDの生パケットを直接解析しません。

## 参照資料
- https://github.com/dekuNukem/Nintendo_Switch_Reverse_Engineering/blob/master/bluetooth_hid_notes.md
- https://github.com/dekuNukem/Nintendo_Switch_Reverse_Engineering/blob/master/bluetooth_hid_subcommands_notes.md
