"use strict";

sap.ui.define(["./BaseController", "sap/ui/Device", "sap/ui/model/json/JSONModel"], function (__BaseController, Device, JSONModel) {
  "use strict";

  function _interopRequireDefault(obj) {
    return obj && obj.__esModule && typeof obj.default !== "undefined" ? obj.default : obj;
  }
  const BaseController = _interopRequireDefault(__BaseController);
  /**
   * @namespace com.optrabot.ui.controller
   */
  const App = BaseController.extend("com.optrabot.ui.controller.App", {
    onInit: function _onInit() {
      // apply content density mode to root view
      this.getView().addStyleClass(this.getOwnerComponent().getContentDensityClass());

      // if the app starts on desktop devices with small or medium screen size, collaps the side navigation
      if (Device.resize.width <= 1024) {
        this.onSideNavButtonPress();
      }
      var environment = window.environment || "PROD";
      var backendBaseUrl = "";
      backendBaseUrl = window.location.origin;
      if (environment !== "PROD") {
        // In development the backend uses a different port
        backendBaseUrl = backendBaseUrl.slice(0, backendBaseUrl.lastIndexOf(":"));
        backendBaseUrl = backendBaseUrl + ":8080";
      }
      const globalData = {
        "backendBaseUrl": backendBaseUrl,
        "appVersion": "1.0.0"
      };
      const globalModel = new JSONModel(globalData);
      this.getOwnerComponent().setModel(globalModel, "global");
    },
    getBundleText: function _getBundleText(sI18nKey, aPlaceholderValues) {
      return Promise.resolve(this.getBundleTextByModel(sI18nKey, this.getOwnerComponent().getModel("i18n"), aPlaceholderValues));
    },
    onSideNavButtonPress: function _onSideNavButtonPress() {
      console.log("SideNavButton pressed");
      const oToolPage = this.byId("optrabot_app");
      var bSideExpanded = oToolPage.getSideExpanded();
      oToolPage.setSideExpanded(!bSideExpanded);
      this._setToggleButtonTooltip(!bSideExpanded);
    },
    _setToggleButtonTooltip: async function _setToggleButtonTooltip(bSideExpanded) {
      const oToggleButton = this.byId("sideNavigationToggleButton");
      if (bSideExpanded) {
        oToggleButton.setTooltip(await this.getBundleText("sideNavigationCollapseTooltip"));
      } else {
        oToggleButton.setTooltip(await this.getBundleText("sideNavigationExpandTooltip"));
      }
    }
  });
  return App;
});
//# sourceMappingURL=App-dbg.controller.js.map
