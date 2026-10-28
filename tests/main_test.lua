-- Lightweight test for the plugin menus and sponsor dialog without KOReader.

local shown_widget
local copied_text
local opened_url

local function extend_class(parent, options)
    options = options or {}
    options.__index = options
    return setmetatable(options, { __index = parent })
end

package.preload["ui/widget/confirmbox"] = function()
    return {}
end

package.preload["datastorage"] = function()
    return {
        getSettingsDir = function() return "/tmp" end,
    }
end

package.preload["device"] = function()
    return {
        canOpenLink = function() return false end,
        openLink = function(_, url) opened_url = url end,
        input = {
            setClipboardText = function(_, text) copied_text = text end,
        },
    }
end

package.preload["ui/widget/infomessage"] = function()
    local InfoMessage = {}
    function InfoMessage:new(options)
        options.is_info_message = true
        return options
    end
    return InfoMessage
end

package.preload["luasettings"] = function()
    local LuaSettings = {}
    function LuaSettings:open()
        return {
            readSetting = function() end,
            saveSetting = function() end,
            delSetting = function() end,
            flush = function() end,
        }
    end
    return LuaSettings
end

package.preload["ui/uimanager"] = function()
    return {
        show = function(_, widget) shown_widget = widget end,
        close = function() shown_widget = nil end,
        nextTick = function(_, callback) callback() end,
        scheduleIn = function(_, _, callback) callback() end,
        askForRestart = function() end,
    }
end

package.preload["ui/widget/container/widgetcontainer"] = function()
    local WidgetContainer = {}
    WidgetContainer.extend = extend_class
    return WidgetContainer
end

package.preload["ffi/util"] = function()
    return {
        template = function(text, ...)
            local values = { ... }
            return (text:gsub("%%(%d+)", function(index)
                return tostring(values[tonumber(index)] or "")
            end))
        end,
    }
end

package.preload["logger"] = function()
    return { warn = function() end }
end

package.preload["gettext"] = function()
    return function(text) return text end
end

package.preload["ui/widget/buttondialog"] = function()
    local ButtonDialog = {}
    function ButtonDialog:new(options)
        options.is_button_dialog = true
        return options
    end
    return ButtonDialog
end

package.preload["ui/widget/qrmessage"] = function()
    local QRMessage = {}
    function QRMessage:new(options)
        options.is_qr_message = true
        return options
    end
    return QRMessage
end

local Device = require("device")
local Mac1984 = assert(loadfile(arg[1] or "plugin/main.lua"))()
local plugin = Mac1984:extend{
    path = "plugin",
    version = "1.2.2",
    github = "hytaoist/mac1984-koreader",
    sponsor_url = "https://example.com/sponsor",
    deploy = {
        deployed_version = function() return "1.2.2" end,
    },
}

local function find_button(dialog, label)
    for _, row in ipairs(dialog.buttons or {}) do
        for _, button in ipairs(row) do
            if button.text == label then return button end
        end
    end
end

plugin:showAbout()
assert(shown_widget and shown_widget.is_button_dialog, "About did not open a button dialog")
local sponsor_button = assert(
    find_button(shown_widget, "Sponsor this project"),
    "About is missing the sponsor module"
)

sponsor_button.callback()
assert(shown_widget and shown_widget.is_button_dialog, "Sponsor dialog did not open")
local qr_button = assert(find_button(shown_widget, "Show QR code"), "Sponsor QR button missing")
local copy_button = assert(find_button(shown_widget, "Copy link"), "Sponsor copy button missing")
assert(find_button(shown_widget, "Open sponsor page in browser") == nil,
    "Browser button should be hidden when the device cannot open links")

qr_button.callback()
assert(shown_widget and shown_widget.is_qr_message, "Sponsor QR code did not open")
assert(shown_widget.text == plugin.sponsor_url, "Sponsor QR code has the wrong URL")

copy_button.callback()
assert(copied_text == plugin.sponsor_url, "Sponsor link was not copied")
assert(shown_widget and shown_widget.is_info_message, "Copy confirmation was not shown")

Device.canOpenLink = function() return true end
plugin:showSponsor()
local browser_button = assert(
    find_button(shown_widget, "Open sponsor page in browser"),
    "Browser button is missing on capable devices"
)
browser_button.callback()
assert(opened_url == plugin.sponsor_url, "Sponsor page was not opened")

print("main test OK")
