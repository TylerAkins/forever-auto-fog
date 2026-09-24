local addonName, ns = ...

local ADDON_PREFIX = "|cff70d6ffForever Auto Fog:|r "
local FOG_CVAR = "volumeFog"
local frame = CreateFrame("Frame")

ns.db = nil
ns.currentMapID = nil
ns.currentMapName = nil

local function Print(message)
    DEFAULT_CHAT_FRAME:AddMessage(ADDON_PREFIX .. message)
end

local function IsMapInfo(info)
    return info and info.mapID and info.name and info.mapType == Enum.UIMapType.Zone
end

function ns.GetCurrentZone()
    local mapID = C_Map.GetBestMapForUnit("player")
    if not mapID then
        return nil, nil
    end

    local info = C_Map.GetMapInfo(mapID)
    if not IsMapInfo(info) or ns.CityMapIDs[mapID] then
        return nil, nil
    end
    return mapID, info.name
end

function ns.GetPreference(mapID)
    if not mapID or not ns.db then
        return true
    end
    local preference = ns.db.zoneSettings[mapID]
    if preference == nil then
        return true
    end
    return preference
end

function ns.SetPreference(mapID, enabled)
    if not mapID or not ns.db then
        return
    end
    ns.db.zoneSettings[mapID] = enabled and true or false
end

function ns.ApplyCurrentZone()
    local mapID, name = ns.GetCurrentZone()
    ns.currentMapID = mapID
    ns.currentMapName = name
    if not mapID then
        return
    end

    local desired = ns.GetPreference(mapID) and "1" or "0"
    if C_CVar.GetCVar(FOG_CVAR) ~= desired then
        C_CVar.SetCVar(FOG_CVAR, desired)
    end

    if ns.RefreshOptions then
        ns.RefreshOptions()
    end
end

function ns.SetCurrentPreference(enabled)
    local mapID, name = ns.GetCurrentZone()
    if not mapID then
        Print("No outdoor zone map is currently available.")
        return false
    end
    ns.SetPreference(mapID, enabled)
    ns.currentMapID = mapID
    ns.currentMapName = name
    ns.ApplyCurrentZone()
    return true
end

function ns.ResetAll()
    ns.db.zoneSettings = {}
    ns.ApplyCurrentZone()
    if ns.RefreshOptions then
        ns.RefreshOptions()
    end
end

function ns.SetAllPreferences(enabled)
    for mapID in pairs(ns.KnownOutdoorMapIDs) do
        ns.SetPreference(mapID, enabled)
    end
    ns.ApplyCurrentZone()
    if ns.RefreshOptions then
        ns.RefreshOptions()
    end
end

local function HandleCommand(input)
    input = (input or ""):lower():match("^%s*(.-)%s*$")
    if input == "" then
        ns.OpenOptions()
    elseif input == "on" then
        if ns.SetCurrentPreference(true) then Print("Fog enabled for this zone.") end
    elseif input == "off" then
        if ns.SetCurrentPreference(false) then Print("Fog disabled for this zone.") end
    elseif input == "reset" then
        ns.ResetAll()
        Print("All zone preferences reset to enabled.")
    elseif input == "status" then
        local mapID, name = ns.GetCurrentZone()
        if mapID then
            Print(string.format("%s (map %d): saved %s, volumeFog %s.", name, mapID,
                ns.GetPreference(mapID) and "enabled" or "disabled",
                C_CVar.GetCVar(FOG_CVAR) or "unknown"))
        else
            Print("No outdoor zone map is currently available.")
        end
    else
        Print("/faf, /faf on, /faf off, /faf status, /faf reset")
    end
end

SLASH_FOREVERAUTOFOG1 = "/faf"
SLASH_FOREVERAUTOFOG2 = "/foreverautofog"
SlashCmdList.FOREVERAUTOFOG = HandleCommand

frame:RegisterEvent("ADDON_LOADED")
frame:RegisterEvent("PLAYER_LOGIN")
frame:RegisterEvent("ZONE_CHANGED")
frame:RegisterEvent("ZONE_CHANGED_INDOORS")
frame:RegisterEvent("ZONE_CHANGED_NEW_AREA")
frame:SetScript("OnEvent", function(_, event, loadedAddon)
    if event == "ADDON_LOADED" then
        if loadedAddon ~= addonName then return end
        ForeverAutoFogDB = ForeverAutoFogDB or {}
        ForeverAutoFogDB.zoneSettings = ForeverAutoFogDB.zoneSettings or {}
        ns.db = ForeverAutoFogDB
        return
    end

    if event == "PLAYER_LOGIN" then
        ns.CreateOptions()
    end
    ns.ApplyCurrentZone()
end)
