local addonName, ns = ...

-- UiMapIDs for the outdoor zone maps shipped by the Classic client.  The names
-- come from C_Map at runtime so the UI is localized.  Cities and instances are
-- intentionally absent: fog is a world-zone setting and their map types do not
-- represent the outdoor areas this addon controls.
ns.ZoneGroups = {
    {
        name = "Eastern Kingdoms",
        mapIDs = {
            1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425,
            1426, 1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435,
            1436, 1437,
        },
    },
    {
        name = "Kalimdor",
        mapIDs = {
            1411, 1412, 1413, 1438, 1439, 1440, 1441, 1442, 1443, 1444,
            1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452,
        },
    },
}

ns.KnownOutdoorMapIDs = {}
for _, group in ipairs(ns.ZoneGroups) do
    for _, mapID in ipairs(group.mapIDs) do
        ns.KnownOutdoorMapIDs[mapID] = true
    end
end

-- Classic capital-city maps are Zone map types, so mapType alone cannot
-- distinguish them from outdoor zones. Keep this explicit list separate from
-- preferences; cities are intentionally not supported by this addon.
ns.CityMapIDs = {
    [1453] = true, [1454] = true, [1455] = true,
    [1456] = true, [1457] = true, [1458] = true,
}

-- The static list above deliberately uses only verified UiMapIDs.  Forever
-- adds world maps over time; Core.lua discovers a player's actual UiMapID and
-- keeps it configurable without guessing an ID from a display name.
