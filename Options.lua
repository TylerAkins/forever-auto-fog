local addonName, ns = ...

local panel
local category
local checkboxes = {}

local function AddText(parent, text, x, y, width)
    local label = parent:CreateFontString(nil, "ARTWORK", "GameFontHighlight")
    label:SetPoint("TOPLEFT", x, y)
    label:SetWidth(width)
    label:SetJustifyH("LEFT")
    label:SetText(text)
    return label
end

local function SortedZoneRows()
    local rows = {}
    for _, group in ipairs(ns.ZoneGroups) do
        local zones = {}
        for _, mapID in ipairs(group.mapIDs) do
            local info = C_Map.GetMapInfo(mapID)
            if info and info.name and info.mapType == Enum.UIMapType.Zone then
                table.insert(zones, { mapID = mapID, name = info.name })
            end
        end
        table.sort(zones, function(left, right) return left.name < right.name end)
        if #zones > 0 then table.insert(rows, { group = group.name, zones = zones }) end
    end

    local mapID, name = ns.GetCurrentZone()
    local known = false
    for _, group in ipairs(rows) do
        for _, zone in ipairs(group.zones) do
            if zone.mapID == mapID then known = true end
        end
    end
    if mapID and not known then
        table.insert(rows, { group = "Forever / newly discovered", zones = {{ mapID = mapID, name = name }} })
    end
    return rows
end

function ns.RefreshOptions()
    for mapID, checkbox in pairs(checkboxes) do
        checkbox:SetChecked(ns.GetPreference(mapID))
    end
end

local function AddCheckbox(parent, zone, y)
    local checkbox = CreateFrame("CheckButton", nil, parent, "UICheckButtonTemplate")
    checkbox:SetPoint("TOPLEFT", 12, y)
    checkbox.Text:SetText(zone.name .. ": Enable Fog")
    checkbox:SetChecked(ns.GetPreference(zone.mapID))
    checkbox:SetScript("OnClick", function(self)
        ns.SetPreference(zone.mapID, self:GetChecked())
        if zone.mapID == ns.currentMapID then ns.ApplyCurrentZone() end
    end)
    checkboxes[zone.mapID] = checkbox
end

function ns.CreateOptions()
    if panel then return end
    panel = CreateFrame("Frame", addonName .. "Options", UIParent)
    panel.name = "Forever Auto Fog"
    AddText(panel, "Forever Auto Fog", 16, -16, 600):SetFontObject("GameFontNormalLarge")
    AddText(panel, "Automatically applies your saved volumetric-fog preference whenever you enter an outdoor zone.", 16, -44, 600)
    AddText(panel, "Enable Fog", 16, -78, 600):SetFontObject("GameFontNormalLarge")

    local reset = CreateFrame("Button", nil, panel, "UIPanelButtonTemplate")
    reset:SetSize(160, 22)
    reset:SetPoint("TOPRIGHT", -24, -76)
    reset:SetText("Reset All to Default")
    reset:SetScript("OnClick", ns.ResetAll)

    local scroll = CreateFrame("ScrollFrame", nil, panel, "UIPanelScrollFrameTemplate")
    scroll:SetPoint("TOPLEFT", 16, -112)
    scroll:SetPoint("BOTTOMRIGHT", -32, 16)
    local content = CreateFrame("Frame", nil, scroll)
    content:SetSize(1, 1)
    scroll:SetScrollChild(content)

    local y = -4
    for _, group in ipairs(SortedZoneRows()) do
        AddText(content, group.group, 8, y, 500):SetFontObject("GameFontNormal")
        y = y - 24
        for _, zone in ipairs(group.zones) do
            AddCheckbox(content, zone, y)
            y = y - 26
        end
        y = y - 8
    end
    content:SetHeight(-y + 8)

    if Settings and Settings.RegisterCanvasLayoutCategory then
        category = Settings.RegisterCanvasLayoutCategory(panel, panel.name)
        Settings.RegisterAddOnCategory(category)
    else
        InterfaceOptions_AddCategory(panel)
    end
end

function ns.OpenOptions()
    if not panel then ns.CreateOptions() end
    if Settings and category then
        Settings.OpenToCategory(category.ID)
    else
        InterfaceOptionsFrame_OpenToCategory(panel)
        InterfaceOptionsFrame_OpenToCategory(panel)
    end
end
