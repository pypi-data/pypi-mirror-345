var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });
import { defineComponent, computed, resolveDirective, openBlock, createBlock, withCtx, createBaseVNode, toDisplayString, createVNode, unref, createElementBlock, createCommentVNode, normalizeClass, createTextVNode, withDirectives } from "./vendor-vue-B7YUw5vA.js";
import { script$10 as script, script$52 as script$1, script$2, script$29 as script$3, script$19 as script$4 } from "./vendor-primevue-C1Wk8Hqm.js";
import { useDialogService, useFirebaseAuthStore, useCommandStore } from "./index-BbFS9DHe.js";
import "./vendor-vue-i18n-CdFxvEOa.js";
const _hoisted_1 = { class: "flex flex-col h-full" };
const _hoisted_2 = { class: "text-2xl font-bold mb-2" };
const _hoisted_3 = {
  key: 0,
  class: "flex flex-col gap-2"
};
const _hoisted_4 = { class: "flex flex-col gap-0.5" };
const _hoisted_5 = { class: "font-medium" };
const _hoisted_6 = { class: "text-muted" };
const _hoisted_7 = { class: "flex flex-col gap-0.5" };
const _hoisted_8 = { class: "font-medium" };
const _hoisted_9 = ["href"];
const _hoisted_10 = { class: "flex flex-col gap-0.5" };
const _hoisted_11 = { class: "font-medium" };
const _hoisted_12 = { class: "text-muted flex items-center gap-1" };
const _hoisted_13 = {
  key: 1,
  class: "flex flex-col gap-4"
};
const _hoisted_14 = { class: "text-gray-600" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "UserPanel",
  setup(__props) {
    const dialogService = useDialogService();
    const authStore = useFirebaseAuthStore();
    const commandStore = useCommandStore();
    const user = computed(() => authStore.currentUser);
    const loading = computed(() => authStore.loading);
    const providerName = computed(() => {
      const providerId = user.value?.providerData[0]?.providerId;
      if (providerId?.includes("google")) {
        return "Google";
      }
      if (providerId?.includes("github")) {
        return "GitHub";
      }
      return providerId;
    });
    const providerIcon = computed(() => {
      const providerId = user.value?.providerData[0]?.providerId;
      if (providerId?.includes("google")) {
        return "pi pi-google";
      }
      if (providerId?.includes("github")) {
        return "pi pi-github";
      }
      return "pi pi-user";
    });
    const isEmailProvider = computed(() => {
      const providerId = user.value?.providerData[0]?.providerId;
      return providerId === "password";
    });
    const handleSignOut = /* @__PURE__ */ __name(async () => {
      await commandStore.execute("Comfy.User.SignOut");
    }, "handleSignOut");
    const handleSignIn = /* @__PURE__ */ __name(async () => {
      await commandStore.execute("Comfy.User.OpenSignInDialog");
    }, "handleSignIn");
    return (_ctx, _cache) => {
      const _directive_tooltip = resolveDirective("tooltip");
      return openBlock(), createBlock(unref(script$4), {
        value: "User",
        class: "user-settings-container h-full"
      }, {
        default: withCtx(() => [
          createBaseVNode("div", _hoisted_1, [
            createBaseVNode("h2", _hoisted_2, toDisplayString(_ctx.$t("userSettings.title")), 1),
            createVNode(unref(script), { class: "mb-3" }),
            user.value ? (openBlock(), createElementBlock("div", _hoisted_3, [
              user.value.photoURL ? (openBlock(), createBlock(unref(script$1), {
                key: 0,
                image: user.value.photoURL,
                shape: "circle",
                size: "large",
                "aria-label": "User Avatar"
              }, null, 8, ["image"])) : createCommentVNode("", true),
              createBaseVNode("div", _hoisted_4, [
                createBaseVNode("h3", _hoisted_5, toDisplayString(_ctx.$t("userSettings.name")), 1),
                createBaseVNode("div", _hoisted_6, toDisplayString(user.value.displayName || _ctx.$t("userSettings.notSet")), 1)
              ]),
              createBaseVNode("div", _hoisted_7, [
                createBaseVNode("h3", _hoisted_8, toDisplayString(_ctx.$t("userSettings.email")), 1),
                createBaseVNode("a", {
                  href: "mailto:" + user.value.email,
                  class: "hover:underline"
                }, toDisplayString(user.value.email), 9, _hoisted_9)
              ]),
              createBaseVNode("div", _hoisted_10, [
                createBaseVNode("h3", _hoisted_11, toDisplayString(_ctx.$t("userSettings.provider")), 1),
                createBaseVNode("div", _hoisted_12, [
                  createBaseVNode("i", {
                    class: normalizeClass(providerIcon.value)
                  }, null, 2),
                  createTextVNode(" " + toDisplayString(providerName.value) + " ", 1),
                  isEmailProvider.value ? withDirectives((openBlock(), createBlock(unref(script$2), {
                    key: 0,
                    icon: "pi pi-pen-to-square",
                    severity: "secondary",
                    text: "",
                    onClick: _cache[0] || (_cache[0] = ($event) => unref(dialogService).showUpdatePasswordDialog())
                  }, null, 512)), [
                    [_directive_tooltip, {
                      value: _ctx.$t("userSettings.updatePassword"),
                      showDelay: 300
                    }]
                  ]) : createCommentVNode("", true)
                ])
              ]),
              loading.value ? (openBlock(), createBlock(unref(script$3), {
                key: 1,
                class: "w-8 h-8 mt-4",
                style: { "--pc-spinner-color": "#000" }
              })) : (openBlock(), createBlock(unref(script$2), {
                key: 2,
                class: "mt-4 w-32",
                severity: "secondary",
                label: _ctx.$t("auth.signOut.signOut"),
                icon: "pi pi-sign-out",
                onClick: handleSignOut
              }, null, 8, ["label"]))
            ])) : (openBlock(), createElementBlock("div", _hoisted_13, [
              createBaseVNode("p", _hoisted_14, toDisplayString(_ctx.$t("auth.login.title")), 1),
              createVNode(unref(script$2), {
                class: "w-52",
                severity: "primary",
                loading: loading.value,
                label: _ctx.$t("auth.login.signInOrSignUp"),
                icon: "pi pi-user",
                onClick: handleSignIn
              }, null, 8, ["loading", "label"])
            ]))
          ])
        ]),
        _: 1
      });
    };
  }
});
export {
  _sfc_main as default
};
//# sourceMappingURL=UserPanel-CXaRl3Vk.js.map
