# dsh-device-bridge

> Optional companion to [dsh-wsl-kit](https://github.com/173787247/dsh-wsl-kit). Not in `install.sh`.

通用 **Companion 协议** 客户端：手机 / IoT / 跳板机薄 Agent，实现 `/v1/health` + `/v1/invoke` 即可接入。与 [dsh-mac-companion](https://github.com/173787247/dsh-mac-companion) 共用协议；SSH 直连用 [dsh-remote-ssh](https://github.com/173787247/dsh-remote-ssh)。

[English → README.en.md](./README.en.md)

## 兼容性

| 字段 | 值 |
|------|----|
| **插件** | `dsh-device-bridge` **0.1.1** |
| **最低 dsh** | ≥ **0.1.2** |
| **最新验证** | 以 [dsh-wsl-kit 兼容性](https://github.com/173787247/dsh-wsl-kit#compatibility-2026-09) 为准（当前 **`0.1.7-alpha.2`**） |
| **套件档位** | 可选（远程桥接） |

## 工具

| 工具 | 作用 |
|------|------|
| `device_list` | 列出已配置设备 |
| `device_status` | GET /v1/health |
| `device_invoke` | POST /v1/invoke（action 白名单） |

## 安装

```sh
dsh plugin --profile web add github:173787247/dsh-device-bridge
python3 companion/mock_server.py --port 18766 --kind phone
```

配置见 `examples/devices.cordis.snippet.yml`。协议：[`docs/PROTOCOL.md`](./docs/PROTOCOL.md)。

### Termux / 轻量 companion

手机上可用 stdlib 样例（健康检查 + ping/notify 桩）：

```sh
python3 examples/termux-companion.py --port 18767
# Termux: 允许局域网访问后，在 dsh 侧配置 baseUrl=http://<phone-ip>:18767
```

手机聊天入口仍用 [dsh-wsl-im](https://github.com/173787247/dsh-wsl-im)；本插件负责设备侧能力。`lib/companion_client.js` 从 [dsh-wsl-common](https://github.com/173787247/dsh-wsl-common) 再导出。

## License

MIT
