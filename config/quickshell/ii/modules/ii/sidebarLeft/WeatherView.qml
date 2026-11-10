pragma ComponentBehavior: Bound;
import qs
import qs.services
import qs.modules.common
import qs.modules.common.widgets
import qs.modules.common.functions
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import Quickshell

Item {
    id: root
    property real padding: 10

    property string cityName: "Lahore, Pakistan"
    property real latitude: 31.5204
    property real longitude: 74.3587
    property string timezone: "Asia/Karachi"

    property bool loading: false
    property string errorMessage: ""
    property string lastUpdated: ""

    // Current weather data
    property real currentTemp: 0
    property real feelsLike: 0
    property int humidity: 0
    property real windSpeed: 0
    property string windDirection: "N"
    property real pressure: 1013
    property real uvIndex: 0
    property string conditionText: "Clear"
    property string iconName: "weather-sunny-symbolic"
    property int isDay: 1
    property real highTemp: 0
    property real lowTemp: 0
    property string sunriseTime: "06:30"
    property string sunsetTime: "17:15"

    // 5-day daily forecast
    property var dailyForecast: []

    // OpenWeather API key
    property string openWeatherApiKey: Persistent.states?.weather?.openWeatherKey || ""

    function weatherCodeToInfo(code, isDaytime) {
        switch (code) {
            case 0:
                return {
                    text: isDaytime ? Translation.tr("Clear Sky") : Translation.tr("Clear Night"),
                    icon: isDaytime ? "weather-sunny-symbolic" : "weather-clear-night-symbolic"
                };
            case 1:
            case 2:
                return {
                    text: Translation.tr("Partly Cloudy"),
                    icon: "weather-partly-cloudy-symbolic"
                };
            case 3:
                return {
                    text: Translation.tr("Overcast"),
                    icon: "weather-cloudy-symbolic"
                };
            case 45:
            case 48:
                return {
                    text: Translation.tr("Haze / Smog / Fog"),
                    icon: "weather-foggy-symbolic"
                };
            case 51:
            case 53:
            case 55:
                return {
                    text: Translation.tr("Drizzle"),
                    icon: "weather-rainy-symbolic"
                };
            case 61:
            case 63:
            case 65:
            case 80:
            case 81:
            case 82:
                return {
                    text: Translation.tr("Rain Showers"),
                    icon: "weather-rainy-symbolic"
                };
            case 71:
            case 73:
            case 75:
            case 85:
            case 86:
                return {
                    text: Translation.tr("Snow"),
                    icon: "weather-snowy-symbolic"
                };
            case 95:
            case 96:
            case 99:
                return {
                    text: Translation.tr("Thunderstorm"),
                    icon: "weather-thunderstorm-symbolic"
                };
            default:
                return {
                    text: Translation.tr("Partly Cloudy"),
                    icon: "weather-partly-cloudy-symbolic"
                };
        }
    }

    function degreesToCardinal(deg) {
        const directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
        const index = Math.round((deg % 360) / 22.5);
        return directions[index % 16];
    }

    function fetchOpenWeather() {
        root.loading = true;
        root.errorMessage = "";

        // If user configured an OpenWeather API key, call OpenWeatherMap API
        if (root.openWeatherApiKey && root.openWeatherApiKey.trim().length > 0) {
            const owmUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${root.latitude}&lon=${root.longitude}&units=metric&appid=${root.openWeatherApiKey.trim()}`;
            const xhr = new XMLHttpRequest();
            xhr.open("GET", owmUrl);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        try {
                            const data = JSON.parse(xhr.responseText);
                            root.currentTemp = Math.round(data.main.temp);
                            root.feelsLike = Math.round(data.main.feels_like);
                            root.highTemp = Math.round(data.main.temp_max);
                            root.lowTemp = Math.round(data.main.temp_min);
                            root.humidity = data.main.humidity;
                            root.pressure = data.main.pressure;
                            root.windSpeed = Math.round(data.wind.speed * 3.6); // km/h
                            root.windDirection = root.degreesToCardinal(data.wind.deg || 0);
                            root.conditionText = data.weather[0].main;

                            const iconCode = data.weather[0].icon || "01d";
                            const isD = iconCode.includes("d");
                            root.isDay = isD ? 1 : 0;
                            if (iconCode.startsWith("01")) root.iconName = isD ? "weather-sunny-symbolic" : "weather-clear-night-symbolic";
                            else if (iconCode.startsWith("02") || iconCode.startsWith("03")) root.iconName = "weather-partly-cloudy-symbolic";
                            else if (iconCode.startsWith("04")) root.iconName = "weather-cloudy-symbolic";
                            else if (iconCode.startsWith("09") || iconCode.startsWith("10")) root.iconName = "weather-rainy-symbolic";
                            else if (iconCode.startsWith("11")) root.iconName = "weather-thunderstorm-symbolic";
                            else if (iconCode.startsWith("13")) root.iconName = "weather-snowy-symbolic";
                            else if (iconCode.startsWith("50")) root.iconName = "weather-foggy-symbolic";
                            else root.iconName = "weather-partly-cloudy-symbolic";

                            const d = new Date();
                            root.lastUpdated = (d.getHours() < 10 ? "0" : "") + d.getHours() + ":" + (d.getMinutes() < 10 ? "0" : "") + d.getMinutes();
                            root.loading = false;
                            return;
                        } catch (e) {
                            // Fallback to Open-Meteo
                        }
                    }
                    fetchOpenMeteo();
                }
            };
            try {
                xhr.send();
                return;
            } catch (err) {
                // Fallback
            }
        }

        fetchOpenMeteo();
    }

    function fetchOpenMeteo() {
        const url = `https://api.open-meteo.com/v1/forecast?latitude=${root.latitude}&longitude=${root.longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m,wind_direction_10m,surface_pressure&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max&timezone=Asia%2FKarachi`;
        const xhr = new XMLHttpRequest();
        xhr.open("GET", url);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                root.loading = false;
                if (xhr.status === 200) {
                    try {
                        const data = JSON.parse(xhr.responseText);
                        const cur = data.current;
                        root.currentTemp = Math.round(cur.temperature_2m);
                        root.feelsLike = Math.round(cur.apparent_temperature);
                        root.humidity = cur.relative_humidity_2m;
                        root.windSpeed = Math.round(cur.wind_speed_10m);
                        root.windDirection = root.degreesToCardinal(cur.wind_direction_10m);
                        root.pressure = Math.round(cur.surface_pressure);
                        root.isDay = cur.is_day;

                        const info = root.weatherCodeToInfo(cur.weather_code, cur.is_day === 1);
                        root.conditionText = info.text;
                        root.iconName = info.icon;

                        const daily = data.daily;
                        if (daily && daily.time && daily.time.length > 0) {
                            root.highTemp = Math.round(daily.temperature_2m_max[0]);
                            root.lowTemp = Math.round(daily.temperature_2m_min[0]);
                            root.uvIndex = daily.uv_index_max ? daily.uv_index_max[0] : 0;
                            if (daily.sunrise) root.sunriseTime = daily.sunrise[0].split("T")[1] || "06:30";
                            if (daily.sunset) root.sunsetTime = daily.sunset[0].split("T")[1] || "17:15";

                            const days = [];
                            const weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
                            for (let i = 0; i < Math.min(5, daily.time.length); i++) {
                                const dateObj = new Date(daily.time[i]);
                                const dayName = (i === 0) ? Translation.tr("Today") : weekdays[dateObj.getDay()];
                                const dayInfo = root.weatherCodeToInfo(daily.weather_code[i], true);
                                days.push({
                                    day: dayName,
                                    max: Math.round(daily.temperature_2m_max[i]),
                                    min: Math.round(daily.temperature_2m_min[i]),
                                    icon: dayInfo.icon,
                                    condition: dayInfo.text
                                });
                            }
                            root.dailyForecast = days;
                        }

                        const d = new Date();
                        root.lastUpdated = (d.getHours() < 10 ? "0" : "") + d.getHours() + ":" + (d.getMinutes() < 10 ? "0" : "") + d.getMinutes();
                    } catch (e) {
                        root.errorMessage = Translation.tr("Error parsing weather data");
                    }
                } else {
                    root.errorMessage = Translation.tr("Unable to fetch weather (%1)").arg(xhr.status);
                }
            }
        };
        try {
            xhr.send();
        } catch (err) {
            root.loading = false;
            root.errorMessage = Translation.tr("Network error");
        }
    }

    Component.onCompleted: {
        root.fetchOpenWeather();
    }

    ScrollView {
        anchors.fill: parent
        clip: true
        contentWidth: availableWidth

        ColumnLayout {
            width: parent.width
            anchors.margins: root.padding
            spacing: 12

            // Top Header: City & Refresh
            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                MaterialSymbol {
                    iconSize: Appearance.font.pixelSize.larger
                    text: "location_on"
                    color: Appearance.colors.colPrimary
                }

                ColumnLayout {
                    spacing: 1
                    StyledText {
                        text: root.cityName
                        font.pixelSize: Appearance.font.pixelSize.normal
                        font.weight: Font.Bold
                        color: Appearance.colors.colOnLayer1
                    }
                    StyledText {
                        text: Translation.tr("Updated: %1").arg(root.lastUpdated.length > 0 ? root.lastUpdated : "--:--")
                        font.pixelSize: Appearance.font.pixelSize.smaller
                        color: Appearance.colors.colSubtext
                    }
                }

                Item { Layout.fillWidth: true }

                RippleButton {
                    implicitWidth: 36
                    implicitHeight: 36
                    buttonRadius: Appearance.rounding.full
                    colBackground: Appearance.colors.colLayer2
                    colBackgroundHover: Appearance.colors.colLayer2Hover
                    colRipple: Appearance.colors.colLayer2Active

                    contentItem: MaterialSymbol {
                        anchors.centerIn: parent
                        iconSize: Appearance.font.pixelSize.normal
                        text: "refresh"
                        color: Appearance.colors.colOnLayer1
                    }

                    onClicked: {
                        root.fetchOpenWeather();
                    }
                }
            }

            // Main Weather Hero Card
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: heroContent.implicitHeight + 24
                radius: Appearance.rounding.normal
                color: Appearance.colors.colLayer2

                ColumnLayout {
                    id: heroContent
                    anchors {
                        left: parent.left
                        right: parent.right
                        top: parent.top
                        margins: 12
                    }
                    spacing: 8

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 16

                        // Vector Weather Icon (Matching Navbar Ricing Theme)
                        CustomIcon {
                            id: weatherVecIcon
                            width: 64
                            height: 64
                            source: root.iconName
                            colorize: true
                            color: Appearance.colors.colPrimary
                        }

                        ColumnLayout {
                            spacing: 2
                            RowLayout {
                                spacing: 4
                                StyledText {
                                    text: `${root.currentTemp}°`
                                    font.pixelSize: 42
                                    font.weight: Font.Bold
                                    color: Appearance.colors.colOnLayer1
                                }
                                StyledText {
                                    text: "C"
                                    font.pixelSize: Appearance.font.pixelSize.larger
                                    color: Appearance.colors.colSubtext
                                    Layout.alignment: Qt.AlignTop
                                }
                            }
                            StyledText {
                                text: root.conditionText
                                font.pixelSize: Appearance.font.pixelSize.normal
                                font.weight: Font.DemiBold
                                color: Appearance.colors.colOnLayer1
                            }
                            StyledText {
                                text: Translation.tr("Feels like %1°C  •  H: %2°  L: %3°").arg(root.feelsLike).arg(root.highTemp).arg(root.lowTemp)
                                font.pixelSize: Appearance.font.pixelSize.smaller
                                color: Appearance.colors.colSubtext
                            }
                        }
                    }
                }
            }

            // Metrics Grid (2 columns)
            GridLayout {
                Layout.fillWidth: true
                columns: 2
                rowSpacing: 8
                columnSpacing: 8

                // Humidity
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 64
                    radius: Appearance.rounding.small
                    color: Appearance.colors.colLayer2

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 10

                        MaterialSymbol {
                            iconSize: 26
                            text: "water_drop"
                            color: Appearance.colors.colPrimary
                        }
                        ColumnLayout {
                            spacing: 1
                            StyledText {
                                text: Translation.tr("Humidity")
                                font.pixelSize: Appearance.font.pixelSize.smaller
                                color: Appearance.colors.colSubtext
                            }
                            StyledText {
                                text: `${root.humidity}%`
                                font.pixelSize: Appearance.font.pixelSize.normal
                                font.weight: Font.Bold
                                color: Appearance.colors.colOnLayer1
                            }
                        }
                    }
                }

                // Wind
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 64
                    radius: Appearance.rounding.small
                    color: Appearance.colors.colLayer2

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 10

                        CustomIcon {
                            width: 26
                            height: 26
                            source: "weather-windy-symbolic"
                            colorize: true
                            color: Appearance.colors.colTertiary
                        }
                        ColumnLayout {
                            spacing: 1
                            StyledText {
                                text: Translation.tr("Wind")
                                font.pixelSize: Appearance.font.pixelSize.smaller
                                color: Appearance.colors.colSubtext
                            }
                            StyledText {
                                text: `${root.windSpeed} km/h ${root.windDirection}`
                                font.pixelSize: Appearance.font.pixelSize.small
                                font.weight: Font.Bold
                                color: Appearance.colors.colOnLayer1
                            }
                        }
                    }
                }

                // Pressure
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 64
                    radius: Appearance.rounding.small
                    color: Appearance.colors.colLayer2

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 10

                        MaterialSymbol {
                            iconSize: 26
                            text: "compress"
                            color: Appearance.colors.colSecondary
                        }
                        ColumnLayout {
                            spacing: 1
                            StyledText {
                                text: Translation.tr("Pressure")
                                font.pixelSize: Appearance.font.pixelSize.smaller
                                color: Appearance.colors.colSubtext
                            }
                            StyledText {
                                text: `${root.pressure} hPa`
                                font.pixelSize: Appearance.font.pixelSize.small
                                font.weight: Font.Bold
                                color: Appearance.colors.colOnLayer1
                            }
                        }
                    }
                }

                // UV Index
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 64
                    radius: Appearance.rounding.small
                    color: Appearance.colors.colLayer2

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 10

                        MaterialSymbol {
                            iconSize: 26
                            text: "wb_sunny"
                            color: Appearance.colors.colPrimary
                        }
                        ColumnLayout {
                            spacing: 1
                            StyledText {
                                text: Translation.tr("UV Index")
                                font.pixelSize: Appearance.font.pixelSize.smaller
                                color: Appearance.colors.colSubtext
                            }
                            StyledText {
                                text: `${root.uvIndex}`
                                font.pixelSize: Appearance.font.pixelSize.normal
                                font.weight: Font.Bold
                                color: Appearance.colors.colOnLayer1
                            }
                        }
                    }
                }

                // Sunrise
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 64
                    radius: Appearance.rounding.small
                    color: Appearance.colors.colLayer2

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 10

                        MaterialSymbol {
                            iconSize: 26
                            text: "wb_twilight"
                            color: Appearance.colors.colTertiary
                        }
                        ColumnLayout {
                            spacing: 1
                            StyledText {
                                text: Translation.tr("Sunrise")
                                font.pixelSize: Appearance.font.pixelSize.smaller
                                color: Appearance.colors.colSubtext
                            }
                            StyledText {
                                text: root.sunriseTime
                                font.pixelSize: Appearance.font.pixelSize.small
                                font.weight: Font.Bold
                                color: Appearance.colors.colOnLayer1
                            }
                        }
                    }
                }

                // Sunset
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 64
                    radius: Appearance.rounding.small
                    color: Appearance.colors.colLayer2

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 10

                        MaterialSymbol {
                            iconSize: 26
                            text: "nights_stay"
                            color: Appearance.colors.colSecondary
                        }
                        ColumnLayout {
                            spacing: 1
                            StyledText {
                                text: Translation.tr("Sunset")
                                font.pixelSize: Appearance.font.pixelSize.smaller
                                color: Appearance.colors.colSubtext
                            }
                            StyledText {
                                text: root.sunsetTime
                                font.pixelSize: Appearance.font.pixelSize.small
                                font.weight: Font.Bold
                                color: Appearance.colors.colOnLayer1
                            }
                        }
                    }
                }
            }

            // 5-Day Forecast Header
            StyledText {
                text: Translation.tr("5-Day Forecast")
                font.pixelSize: Appearance.font.pixelSize.normal
                font.weight: Font.Bold
                color: Appearance.colors.colOnLayer1
                Layout.topMargin: 4
            }

            // 5-Day Forecast List
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                Repeater {
                    model: root.dailyForecast
                    delegate: Rectangle {
                        required property var modelData
                        Layout.fillWidth: true
                        implicitHeight: 44
                        radius: Appearance.rounding.small
                        color: Appearance.colors.colLayer2

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 12
                            anchors.rightMargin: 12
                            spacing: 10

                            StyledText {
                                Layout.preferredWidth: 60
                                text: modelData.day
                                font.pixelSize: Appearance.font.pixelSize.small
                                font.weight: Font.DemiBold
                                color: Appearance.colors.colOnLayer1
                            }

                            CustomIcon {
                                width: 22
                                height: 22
                                source: modelData.icon
                                colorize: true
                                color: Appearance.colors.colPrimary
                            }

                            StyledText {
                                Layout.fillWidth: true
                                text: modelData.condition
                                font.pixelSize: Appearance.font.pixelSize.smaller
                                color: Appearance.colors.colSubtext
                                elide: Text.ElideRight
                            }

                            StyledText {
                                text: `${modelData.max}°  /  ${modelData.min}°`
                                font.pixelSize: Appearance.font.pixelSize.small
                                font.weight: Font.DemiBold
                                color: Appearance.colors.colOnLayer1
                            }
                        }
                    }
                }
            }

            // Optional OpenWeather API Key Setting
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: apiKeyCol.implicitHeight + 16
                radius: Appearance.rounding.small
                color: Appearance.colors.colLayer2
                Layout.topMargin: 4

                ColumnLayout {
                    id: apiKeyCol
                    anchors {
                        left: parent.left
                        right: parent.right
                        top: parent.top
                        margins: 10
                    }
                    spacing: 6

                    RowLayout {
                        spacing: 6
                        MaterialSymbol {
                            iconSize: 18
                            text: "key"
                            color: Appearance.colors.colSubtext
                        }
                        StyledText {
                            text: Translation.tr("OpenWeather API Key (Optional)")
                            font.pixelSize: Appearance.font.pixelSize.smaller
                            font.weight: Font.Bold
                            color: Appearance.colors.colSubtext
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        MaterialTextField {
                            id: owmApiKeyInput
                            Layout.fillWidth: true
                            text: root.openWeatherApiKey
                            placeholderText: Translation.tr("Paste OpenWeather API key here...")
                            echoMode: TextInput.Password
                        }

                        RippleButton {
                            implicitWidth: 60
                            implicitHeight: 34
                            buttonRadius: Appearance.rounding.small
                            colBackground: Appearance.colors.colSecondaryContainer

                            contentItem: StyledText {
                                anchors.centerIn: parent
                                text: Translation.tr("Save")
                                font.pixelSize: Appearance.font.pixelSize.smaller
                                color: Appearance.colors.colOnSecondaryContainer
                            }

                            onClicked: {
                                root.openWeatherApiKey = owmApiKeyInput.text.trim();
                                if (!Persistent.states.weather) Persistent.states.weather = {};
                                Persistent.states.weather.openWeatherKey = root.openWeatherApiKey;
                                root.fetchOpenWeather();
                            }
                        }
                    }
                }
            }
        }
    }
}
