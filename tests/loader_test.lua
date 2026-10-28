local plugin_root = assert(arg[1], "plugin path")
local runtime = plugin_root .. "/theme/apply.lua"

package.preload["logger"] = function()
    return { warn = function() end }
end

package.preload["libs/libkoreader-lfs"] = function()
    return {
        attributes = function(path, attribute)
            if path == runtime then
                if attribute then return "file" end
                return { mode = "file" }
            end
        end,
    }
end

package.preload["datastorage"] = function()
    return {
        getDataDir = function() return plugin_root .. "/unused-data" end,
    }
end

package.path = plugin_root .. "/?.lua;" .. package.path
dofile("patches/2-mac1984.lua")

assert(_G.mac1984_loader_test_loaded, "loader did not load the plugin runtime")
print("loader test OK")
