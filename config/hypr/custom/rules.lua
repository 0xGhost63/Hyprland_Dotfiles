-- Custom user window rules

-- QuickNote (Ghost's Notes)
hl.window_rule({ match = { class = "^(hypr\\.quicknote)$" }, float = true })
hl.window_rule({ match = { class = "^(hypr\\.quicknote)$" }, size = {650, 450} })
hl.window_rule({ match = { class = "^(hypr\\.quicknote)$" }, move = {"100%-670", 60} })

-- WiFi Panel
hl.window_rule({ match = { class = "^(hypr\\.wifipanel)$" }, float = true })
hl.window_rule({ match = { class = "^(hypr\\.wifipanel)$" }, size = {320, 480} })
hl.window_rule({ match = { class = "^(hypr\\.wifipanel)$" }, move = {"100%-340", 55} })
hl.window_rule({ match = { class = "^(hypr\\.wifipanel)$" }, border_size = 0 })
hl.window_rule({ match = { class = "^(hypr\\.wifipanel)$" }, no_shadow = true })
hl.window_rule({ match = { class = "^(hypr\\.wifipanel)$" }, pin = true })

-- Bluetooth Panel
hl.window_rule({ match = { class = "^(hypr\\.btpanel)$" }, float = true })
hl.window_rule({ match = { class = "^(hypr\\.btpanel)$" }, size = {320, 480} })
hl.window_rule({ match = { class = "^(hypr\\.btpanel)$" }, move = {"100%-340", 55} })
hl.window_rule({ match = { class = "^(hypr\\.btpanel)$" }, border_size = 0 })
hl.window_rule({ match = { class = "^(hypr\\.btpanel)$" }, no_shadow = true })
hl.window_rule({ match = { class = "^(hypr\\.btpanel)$" }, pin = true })

-- Ghost Desktop Mascot Rules
hl.window_rule({ match = { title = "^(ghost_mascot)$" }, float = true })
hl.window_rule({ match = { title = "^(ghost_mascot)$" }, pin = true })
hl.window_rule({ match = { title = "^(ghost_mascot)$" }, move = {"75%", "55%"} })
hl.window_rule({ match = { title = "^(ghost_mascot)$" }, border_size = 0 })
hl.window_rule({ match = { title = "^(ghost_mascot)$" }, no_blur = true })
hl.window_rule({ match = { title = "^(ghost_mascot)$" }, no_shadow = true })
hl.window_rule({ match = { title = "^(ghost_mascot)$" }, no_initial_focus = true })
hl.window_rule({ match = { title = "^(ghost_mascot)$" }, no_focus = true })

-- Widgets Window Rules
hl.window_rule({ match = { class = "widget_.*" }, float = true })
hl.window_rule({ match = { class = "widget_.*" }, border_size = 0 })
hl.window_rule({ match = { class = "widget_.*" }, no_shadow = true })
hl.window_rule({ match = { class = "widget_.*" }, no_initial_focus = true })
hl.window_rule({ match = { class = "widget_tl" }, workspace = 3 })
hl.window_rule({ match = { class = "widget_tr" }, workspace = 3 })
hl.window_rule({ match = { class = "widget_bottom" }, workspace = 3 })
hl.window_rule({ match = { class = "widget_tl" }, move = {32, 68} })
hl.window_rule({ match = { class = "widget_tl" }, size = {690, 350} })
hl.window_rule({ match = { class = "widget_tr" }, move = {1034, 63} })
hl.window_rule({ match = { class = "widget_tr" }, size = {320, 300} })
hl.window_rule({ match = { class = "widget_bottom" }, move = {32, 457} })
hl.window_rule({ match = { class = "widget_bottom" }, size = {1310, 300} })
