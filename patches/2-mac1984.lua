-- Stable Macintosh 1984 loader.
--
-- Storefront can replace mac1984-koreader.koplugin during an OTA update. This
-- tiny user patch stays in place and always loads the newest available runtime.

local logger = require("logger")
local lfs = require("libs/libkoreader-lfs")

local function is_file(path)
    return lfs.attributes(path, "mode") == "file"
end

local function load_from_plugin_path()
    for entry in package.path:gmatch("[^;]+") do
        local plugin_root = entry:match("^(.*mac1984%-koreader%.koplugin)/")
        if plugin_root then
            local runtime = plugin_root .. "/theme/apply.lua"
            if is_file(runtime) then return runtime end
        end
    end
end

local function load_runtime()
    local runtime = load_from_plugin_path()
    if runtime then return runtime end

    local DataStorage = require("datastorage")
    local data_dir = DataStorage:getDataDir()
    local candidates = {
        data_dir .. "/plugins/mac1984-koreader.koplugin/theme/apply.lua",
        data_dir .. "/.mac1984-theme/runtime/apply.lua",
    }
    for _index, candidate in ipairs(candidates) do
        if is_file(candidate) then return candidate end
    end
end

local runtime = load_runtime()
if not runtime then
    logger.warn("Mac1984: theme runtime not found; install or re-enable the plugin")
    return
end

local ok, err = pcall(dofile, runtime)
if not ok then
    logger.warn("Mac1984: could not load runtime", runtime, err)
end
