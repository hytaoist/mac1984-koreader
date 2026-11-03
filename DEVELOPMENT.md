# 开发与发布

本文档面向修改、构建和维护项目的人。普通安装请阅读 [README.md](README.md)。

## 项目结构

```text
plugin/                          KOReader 插件入口、部署与 OTA
patches/2-mac1984.lua           稳定用户补丁/加载器
plugin/theme/apply.lua          UI 运行时修改
assets/icons/                   KOReader 图标
assets/simpleui-icons/          SimpleUI 图标包
assets/fonts/                   ChicagoFLF 字体
assets/sponsor/                 微信赞赏码
tests/                          自动化测试
dist/                           构建产物
```

安装后，文件分布在：

```text
koreader/plugins/mac1984-koreader.koplugin/   Storefront 管理的插件
koreader/patches/2-mac1984.lua               用户补丁/加载器
koreader/.mac1984-theme/runtime/apply.lua    兼容旧安装的运行时副本
koreader/.mac1984-theme/backup/              原文件备份
koreader/icons/                              KOReader 图标
koreader/fonts/Mac1984Chicago.ttf            UI 字体
koreader/settings/simpleui/sui_icons/packs/Macintosh 1984/
```

插件只使用 KOReader 的公开模块和用户补丁机制。UI 修改均有 `pcall` 保护。

## 构建

```bash
./build.sh
```

输出：

```text
dist/mac1984-koreader-v<version>.koplugin.zip  Storefront Release asset
dist/mac1984-koreader-v<version>.zip           手动安装包
dist/SHA256SUMS
```

Storefront 要求 ZIP 根目录为 `mac1984-koreader.koplugin/`，且目录内包含 `_meta.lua`。
ZIP 使用固定文件顺序、时间戳和权限，因此重复构建会得到相同的 SHA-256。

## 测试

```bash
lua tests/patch_smoke_test.lua plugin/theme/apply.lua
lua tests/main_test.lua plugin/main.lua
lua tests/ota_test.lua plugin/ota.lua
./tests/run_loader_test.sh
./tests/run_deploy_test.sh
./tests/run_installer_test.sh
./tests/run_build_repro_test.sh
```

测试覆盖插件 UI、OTA、首次部署、重复安装、旧版备份迁移、SimpleUI 设置恢复、卸载、
AppleDouble 元数据清理、Storefront ZIP 结构和构建可重复性。

## 发布

1. 修改 `plugin/_meta.lua` 和 `assets/simpleui-icons/pack.lua` 中的版本号。
2. 运行完整测试和 `./build.sh`。
3. 提交代码并创建 `v<version>` 标签。
4. 推送标签，`.github/workflows/release.yml` 会构建并创建 GitHub Release。

也可以运行 `./publish.sh`，但需要本机 `gh` 已完成 GitHub 登录。

## 赞助入口

微信赞赏码由 `plugin/_meta.lua` 中的 `sponsor_wechat_qr` 配置。可选的公开赞助网址由
`sponsor_url` 配置，两者可以独立启用。

## 高级设置

可在 `koreader/settings.reader.lua` 中调整：

```lua
["mac1984_enabled"] = true,
["mac1984_pinstripes"] = false,  -- 关闭标题栏细条纹
["mac1984_shadows"] = false,     -- 关闭窗口硬阴影
```

主题不会替换正文字体。
