-- Macintosh 1984 plugin entry point.
--
-- Storefront owns the plugin directory. This file deploys the theme into
-- stable KOReader locations, exposes repair/toggle controls, and provides an
-- OTA path for sideloaded installations.

local ConfirmBox = require("ui/widget/confirmbox")
local DataStorage = require("datastorage")
local Device = require("device")
local InfoMessage = require("ui/widget/infomessage")
local LuaSettings = require("luasettings")
local UIManager = require("ui/uimanager")
local WidgetContainer = require("ui/widget/container/widgetcontainer")
local ffiutil = require("ffi/util")
local logger = require("logger")
local _ = require("gettext")
local T = ffiutil.template

local Mac1984 = WidgetContainer:extend{
    name = "mac1984",
    is_doc_only = false,
}

local function load_module(path)
    local ok, module = pcall(dofile, path)
    if not ok or type(module) ~= "table" then
        logger.warn("Mac1984: could not load", path, module)
        return nil
    end
    return module
end

local function trim(value)
    return (tostring(value or ""):gsub("^%s+", ""):gsub("%s+$", ""))
end

local function is_web_url(value)
    return type(value) == "string" and value:match("^https?://%S+$") ~= nil
end

local function is_safe_relative_path(value)
    return type(value) == "string"
        and value ~= ""
        and value:sub(1, 1) ~= "/"
        and value:match("(^|/)%.%.(/|$)") == nil
        and value:match("%.[%a%d]+$") ~= nil
end

local function file_exists(path)
    local file = path and io.open(path, "rb")
    if not file then return false end
    file:close()
    return true
end

local function can_open_link()
    local ok, can_open = pcall(function() return Device:canOpenLink() end)
    return ok and can_open == true
end

local function get_button_dialog()
    local ok, ButtonDialog = pcall(require, "ui/widget/buttondialog")
    return ok and ButtonDialog or nil
end

function Mac1984:init()
    local ok_meta, meta = pcall(dofile, self.path .. "/_meta.lua")
    if ok_meta and type(meta) == "table" then
        self.version = meta.version or self.version
        self.github = meta.github or self.github
        self.sponsor_url = is_web_url(meta.sponsor_url) and meta.sponsor_url or nil
        if is_safe_relative_path(meta.sponsor_wechat_qr) then
            local reward_path = self.path .. "/" .. meta.sponsor_wechat_qr
            if file_exists(reward_path) then
                self.wechat_reward_path = reward_path
            else
                logger.warn("Mac1984: could not find WeChat reward image", reward_path)
            end
        end
    end

    self.deploy = load_module(self.path .. "/deploy.lua")
    self.ota = load_module(self.path .. "/ota.lua")
    self.state = LuaSettings:open(DataStorage:getSettingsDir() .. "/mac1984-koreader.lua")

    if self.ui and self.ui.menu then
        self.ui.menu:registerToMainMenu(self)
    end
    UIManager:nextTick(function() self:initializeTheme() end)
end

function Mac1984:initializeTheme()
    if not self.deploy or not self:isThemeEnabled() then return end
    if not self.version then
        logger.warn("Mac1984: plugin version is missing")
        return
    end

    local deployed_before = self.deploy.is_deployed(self.version)
    local runtime_was_loaded = _G._mac1984_theme_loaded == true
    local report, deploy_error = self.deploy.deploy(self.path, self.version)
    if not report then
        logger.warn("Mac1984: deployment failed:", deploy_error)
        if self.state:readSetting("last_error") ~= deploy_error then
            self.state:saveSetting("last_error", deploy_error)
            self.state:flush()
            UIManager:show(InfoMessage:new{
                text = T(_("Macintosh 1984 could not install its theme files.\n\n%1"), tostring(deploy_error)),
                timeout = 6,
            })
        end
        return
    end

    self.state:delSetting("last_error")
    self.state:saveSetting("deployed_version", self.version)
    self.state:saveSetting("last_deployed_at", os.time())
    self.state:flush()

    -- User patches are the preferred startup path, but some KOReader builds
    -- disable or skip them. Load the runtime from the plugin as a fallback
    -- instead of remaining silently unthemed.
    local runtime_loaded = runtime_was_loaded
    local runtime_error = _G._mac1984_theme_error
    if not runtime_loaded then
        runtime_loaded, runtime_error = self:loadThemeRuntime()
    end
    self:recordThemeRuntimeError(runtime_error)

    if deployed_before then return end
    UIManager:scheduleIn(1, function()
        -- On a Storefront update the tiny user patch has usually already loaded
        -- the new runtime. In that case assets were refreshed during this boot
        -- and an extra restart would be unnecessary.
        if runtime_was_loaded then return end
        UIManager:askForRestart(_(
            "Macintosh 1984 theme files are ready.\n\n"
            .. "KOReader needs to restart once to apply the theme and its icons."
        ))
    end)
end

function Mac1984:loadThemeRuntime()
    if _G._mac1984_theme_loaded then return true, _G._mac1984_theme_error end

    local runtime = self.path .. "/theme/apply.lua"
    if not file_exists(runtime) then
        return false, "Theme runtime is missing: " .. runtime
    end

    local ok, load_error = pcall(dofile, runtime)
    if not ok then
        return false, tostring(load_error)
    end
    if not _G._mac1984_theme_loaded then
        return false, _G._mac1984_theme_error
            or "Theme runtime returned without initializing"
    end
    logger.info("Mac1984: compatibility runtime loaded from", runtime)
    return true, _G._mac1984_theme_error
end

function Mac1984:recordThemeRuntimeError(runtime_error)
    if not runtime_error then
        self.state:delSetting("last_theme_error")
        self.state:flush()
        return
    end

    runtime_error = tostring(runtime_error)
    logger.warn("Mac1984: theme runtime error:", runtime_error)
    local previous = self.state:readSetting("last_theme_error")
    self.state:saveSetting("last_theme_error", runtime_error)
    self.state:flush()
    if previous ~= runtime_error then
        UIManager:show(InfoMessage:new{
            text = T(_(
                "Macintosh 1984 could not fully apply its theme runtime.\n\n"
                .. "%1\n\nOpen Tools > Macintosh 1984 > Theme diagnostics for details."
            ), runtime_error),
            timeout = 8,
        })
    end
end

function Mac1984:reinstallTheme()
    if not self.deploy then return end
    self.state:saveSetting("disabled", false)
    self.state:flush()
    local report, deploy_error = self.deploy.deploy(self.path, self.version)
    if not report then
        UIManager:show(InfoMessage:new{
            text = T(_("Could not reinstall the theme files.\n\n%1"), tostring(deploy_error)),
        })
        return
    end
    self.state:saveSetting("deployed_version", self.version)
    self.state:saveSetting("last_deployed_at", os.time())
    self.state:flush()
    UIManager:askForRestart(_(
        "Macintosh 1984 files have been repaired and refreshed.\n\n"
        .. "Restart KOReader to load every icon and the UI font."
    ))
end

function Mac1984:restoreOriginalTheme()
    if not self.deploy then return end
    self.state:saveSetting("disabled", true)
    self.state:flush()
    G_reader_settings:saveSetting("mac1984_enabled", false)
    G_reader_settings:flush()
    self.deploy.uninstall()
    UIManager:askForRestart(_(
        "Macintosh 1984 was disabled and its original files were restored.\n\n"
        .. "The plugin remains installed, so you can enable the theme again from "
        .. "Tools > Macintosh 1984."
    ))
end

function Mac1984:enableTheme()
    self.state:saveSetting("disabled", false)
    G_reader_settings:saveSetting("mac1984_enabled", true)
    G_reader_settings:flush()
    self.state:flush()
    self:reinstallTheme()
end

function Mac1984:isThemeEnabled()
    return self.state:readSetting("disabled") ~= true
        and not G_reader_settings:isFalse("mac1984_enabled")
end

function Mac1984:getThemeDiagnostics()
    local patch_path = "unknown"
    local ok_storage, DataStorageModule = pcall(require, "datastorage")
    if ok_storage and type(DataStorageModule.getPatchesDir) == "function" then
        local ok_dir, directory = pcall(DataStorageModule.getPatchesDir, DataStorageModule)
        if ok_dir and directory then
            patch_path = directory .. "/2-mac1984.lua"
        end
    end

    local patch_status = _("not run")
    local ok_patch, userpatch = pcall(require, "userpatch")
    if ok_patch and type(userpatch) == "table" then
        if type(userpatch.arePatchesDisabled) == "function"
            and userpatch.arePatchesDisabled() then
            patch_status = _("user patches are disabled")
        elseif type(userpatch.execution_status) == "table" then
            local status = userpatch.execution_status["2-mac1984.lua"]
            if status == true then
                patch_status = _("ran successfully")
            elseif status == false then
                patch_status = _("failed")
            end
        end
    end

    local model = "unknown"
    local ok_model, model_name = pcall(Device.getModel, Device)
    if ok_model and model_name then model = tostring(model_name) end

    local runtime_state = _G._mac1984_theme_loaded and _("loaded") or _("not loaded")
    local runtime_error = _G._mac1984_theme_error
        or self.state:readSetting("last_theme_error")
        or _("none")
    local plugin_setting = self:isThemeEnabled() and _("enabled") or _("disabled")
    local patch_file = file_exists(patch_path) and _("present") or _("missing")
    local runtime_file = file_exists(self.path .. "/theme/apply.lua")
        and _("present") or _("missing")

    return table.concat({
        T(_("Device: %1"), model),
        T(_("Plugin: v%1"), self.version or "?"),
        T(_("Installed payload: %1"),
            self.deploy and self.deploy.deployed_version() or _("not installed")),
        T(_("Plugin setting: %1"), plugin_setting),
        T(_("Theme runtime: %1"), runtime_state),
        T(_("Runtime file: %1"), runtime_file),
        T(_("Startup patch: %1"), patch_status),
        T(_("Patch file: %1"), patch_file),
        T(_("Last error: %1"), runtime_error),
    }, "\n")
end

function Mac1984:showDiagnostics()
    UIManager:show(InfoMessage:new{
        text = _("Macintosh 1984 diagnostics") .. "\n\n" .. self:getThemeDiagnostics(),
    })
end

function Mac1984:showAbout()
    local deployed = self.deploy and self.deploy.deployed_version() or _("not installed")
    local text = T(_(
        "Macintosh 1984 for KOReader\n\n"
        .. "Plugin: v%1\n"
        .. "Installed payload: %2\n\n"
        .. "A 1-bit Macintosh interface theme with 103 KOReader icons, "
        .. "34 SimpleUI icons, ChicagoFLF, striped title bars and hard shadows.\n\n"
        .. "Updates: Storefront > Update All, or Tools > Macintosh 1984 > Check for updates.\n\n"
        .. "github.com/hytaoist/mac1984-koreader"
    ), self.version or "?", deployed)

    local ButtonDialog = get_button_dialog()
    if not ButtonDialog then
        if self.sponsor_url then
            text = text .. "\n\n" .. T(_("Sponsor: %1"), self.sponsor_url)
        end
        if self.wechat_reward_path then
            text = text .. "\n\n" .. _("WeChat reward code is available from the Sponsor menu.")
        end
        UIManager:show(InfoMessage:new{ text = text })
        return
    end

    local about_dialog
    local buttons = {}
    if self.sponsor_url or self.wechat_reward_path then
        table.insert(buttons, {{
            text = _("Sponsor this project"),
            callback = function() self:showSponsor() end,
        }})
    end
    table.insert(buttons, {{
        text = _("Close"),
        callback = function() UIManager:close(about_dialog) end,
    }})
    about_dialog = ButtonDialog:new{
        title = text,
        buttons = buttons,
    }
    UIManager:show(about_dialog)
end

function Mac1984:copySponsorLink()
    local copied = false
    if Device.input and Device.input.setClipboardText then
        copied = pcall(Device.input.setClipboardText, Device.input, self.sponsor_url)
    end
    UIManager:show(InfoMessage:new{
        text = copied and _("Sponsor link copied to the clipboard.")
            or T(_("Sponsor link:\n%1"), self.sponsor_url),
        timeout = copied and 2 or nil,
    })
end

function Mac1984:showSponsorQRCode()
    local ok_qr, QRMessage = pcall(require, "ui/widget/qrmessage")
    if not ok_qr or not QRMessage then
        self:copySponsorLink()
        return
    end
    UIManager:show(QRMessage:new{ text = self.sponsor_url })
end

function Mac1984:showWeChatRewardCode()
    if not file_exists(self.wechat_reward_path) then
        UIManager:show(InfoMessage:new{
            text = _("The WeChat reward code is missing from this plugin installation."),
        })
        return
    end

    local ok_viewer, ImageViewer = pcall(require, "ui/widget/imageviewer")
    if not ok_viewer or not ImageViewer then
        UIManager:show(InfoMessage:new{
            text = _("This KOReader version cannot display the built-in reward image."),
        })
        return
    end

    UIManager:show(ImageViewer:new{
        file = self.wechat_reward_path,
        fullscreen = true,
        with_title_bar = true,
        title_text = _("WeChat reward code"),
    })
end

function Mac1984:showSponsor()
    if not self.sponsor_url and not self.wechat_reward_path then
        UIManager:show(InfoMessage:new{
            text = _("A sponsorship method has not been configured."),
        })
        return
    end

    local ButtonDialog = get_button_dialog()
    if not ButtonDialog then
        if self.wechat_reward_path then
            self:showWeChatRewardCode()
        else
            self:showSponsorQRCode()
        end
        return
    end

    local sponsor_dialog
    local buttons = {}
    if self.wechat_reward_path then
        table.insert(buttons, {{
            text = _("Show WeChat reward code"),
            callback = function()
                UIManager:close(sponsor_dialog)
                self:showWeChatRewardCode()
            end,
        }})
    end
    if self.sponsor_url then
        table.insert(buttons, {
            {
                text = _("Show QR code"),
                callback = function()
                    UIManager:close(sponsor_dialog)
                    self:showSponsorQRCode()
                end,
            },
            {
                text = _("Copy link"),
                callback = function()
                    UIManager:close(sponsor_dialog)
                    self:copySponsorLink()
                end,
            },
        })
        if can_open_link() then
            table.insert(buttons, {{
                text = _("Open sponsor page in browser"),
                callback = function()
                    UIManager:close(sponsor_dialog)
                    Device:openLink(self.sponsor_url)
                end,
            }})
        end
    end
    table.insert(buttons, {{
        text = _("Close"),
        callback = function() UIManager:close(sponsor_dialog) end,
    }})

    local sponsor_text = _(
        "Sponsor Macintosh 1984\n\n"
        .. "If this theme saves you time or makes your reading setup more enjoyable, "
        .. "please consider sponsoring its continued maintenance."
    )
    if self.sponsor_url then
        sponsor_text = sponsor_text .. "\n\n" .. self.sponsor_url
    end
    if self.wechat_reward_path then
        sponsor_text = sponsor_text .. "\n\n"
            .. _("WeChat: open the built-in reward code and scan it with WeChat.")
    end

    sponsor_dialog = ButtonDialog:new{
        title = sponsor_text,
        buttons = buttons,
    }
    UIManager:show(sponsor_dialog)
end

function Mac1984:checkForUpdate()
    if not self.ota then
        UIManager:show(InfoMessage:new{ text = _("The OTA module is unavailable.") })
        return
    end

    local ok_network, NetworkMgr = pcall(require, "ui/network/manager")
    if not ok_network or not NetworkMgr then
        UIManager:show(InfoMessage:new{ text = _("Network support is unavailable.") })
        return
    end

    NetworkMgr:runWhenConnected(function()
        UIManager:show(InfoMessage:new{ text = _("Checking for Macintosh 1984 updates..."), timeout = 1 })
        UIManager:scheduleIn(0.1, function()
            local release, fetch_error = self.ota.fetch_latest(self.github)
            if not release then
                UIManager:show(InfoMessage:new{
                    text = T(_("Could not check for updates.\n\n%1"), tostring(fetch_error)),
                    timeout = 6,
                })
                return
            end
            if not self.ota.is_newer(release.version, self.version) then
                UIManager:show(InfoMessage:new{
                    text = T(_("Macintosh 1984 is up to date (v%1)."), self.version),
                })
                return
            end

            UIManager:show(ConfirmBox:new{
                text = T(_(
                    "Macintosh 1984 v%1 is available.\n\nYou have v%2. Download and install it now?"
                ), release.version, self.version),
                ok_text = _("Update"),
                cancel_text = _("Later"),
                ok_callback = function()
                    UIManager:show(InfoMessage:new{ text = _("Downloading update..."), timeout = 1 })
                    UIManager:scheduleIn(0.1, function()
                        local installed, install_error = self.ota.install(
                            self.path, release.url, release.version
                        )
                        if not installed then
                            UIManager:show(InfoMessage:new{
                                text = T(_("Update failed.\n\n%1"), tostring(install_error)),
                                timeout = 6,
                            })
                            return
                        end
                        UIManager:askForRestart(T(_(
                            "Macintosh 1984 was updated to v%1.\n\n"
                            .. "Restart KOReader to load the new version."
                        ), release.version))
                    end)
                end,
            })
        end)
    end)
end

function Mac1984:getSubMenu()
    local items = {
        {
            text = T(_("Version: %1"), self.version or "?"),
            callback = function() self:showAbout() end,
            keep_menu_open = true,
        },
    }

    if self.state:readSetting("disabled") == true then
        table.insert(items, {
            text = _("Enable and install the theme"),
            callback = function()
                UIManager:show(ConfirmBox:new{
                    text = _("Enable Macintosh 1984 and replace the current interface files?"),
                    ok_text = _("Enable"),
                    cancel_text = _("Cancel"),
                    ok_callback = function() self:enableTheme() end,
                })
            end,
        })
    else
        table.insert(items, {
            text = _("Reinstall / repair theme files"),
            callback = function()
                UIManager:show(ConfirmBox:new{
                    text = _("Refresh every icon, font and theme file from this plugin version?"),
                    ok_text = _("Reinstall"),
                    cancel_text = _("Cancel"),
                    ok_callback = function() self:reinstallTheme() end,
                })
            end,
        })
        table.insert(items, {
            text = _("Disable and restore original files"),
            callback = function()
                UIManager:show(ConfirmBox:new{
                    text = _(
                        "Disable Macintosh 1984 and restore the icons and SimpleUI settings "
                        .. "that existed before installation?"
                    ),
                    ok_text = _("Restore"),
                    cancel_text = _("Cancel"),
                    ok_callback = function() self:restoreOriginalTheme() end,
                })
            end,
        })
    end

    table.insert(items, {
        text = _("Check for updates"),
        callback = function() self:checkForUpdate() end,
    })
    table.insert(items, {
        text = _("Theme diagnostics"),
        callback = function() self:showDiagnostics() end,
        keep_menu_open = true,
    })
    table.insert(items, {
        text = _("About"),
        callback = function() self:showAbout() end,
        keep_menu_open = true,
    })
    return items
end

function Mac1984:addToMainMenu(menu_items)
    menu_items.mac1984 = {
        text = _("Macintosh 1984"),
        sorting_hint = "tools",
        sub_item_table_func = function() return self:getSubMenu() end,
    }
end

return Mac1984
