function $e(a, e, n, t) {
  if (e === !1 || e == null || !e && a === "style") return "";
  if (e === !0) return " " + (a + '="' + a + '"');
  var i = typeof e;
  return i !== "object" && i !== "function" || typeof e.toJSON != "function" || (e = e.toJSON()), typeof e == "string" || (e = JSON.stringify(e), n) ? (e = rt(e), " " + a + '="' + e + '"') : " " + a + "='" + e.replace(/'/g, "&#39;") + "'";
}
function rt(a) {
  var e = "" + a, n = ot.exec(e);
  if (!n) return a;
  var t, i, o, c = "";
  for (t = n.index, i = 0; t < e.length; t++) {
    switch (e.charCodeAt(t)) {
      case 34:
        o = "&quot;";
        break;
      case 38:
        o = "&amp;";
        break;
      case 60:
        o = "&lt;";
        break;
      case 62:
        o = "&gt;";
        break;
      default:
        continue;
    }
    i !== t && (c += e.substring(i, t)), i = t + 1, c += o;
  }
  return i !== t ? c + e.substring(i, t) : c;
}
var ot = /["&<>]/;
function Ve(a, e, n, t) {
  if (!(a instanceof Error)) throw a;
  if (!(typeof window > "u" && e || t)) throw a.message += " on line " + n, a;
  var i, o, c, g;
  try {
    t = t || require("fs").readFileSync(e, { encoding: "utf8" }), i = 3, o = t.split(`
`), c = Math.max(n - i, 0), g = Math.min(o.length, n + i);
  } catch (d) {
    return a.message += " - could not read from " + e + " (" + d.message + ")", void Ve(a, null, n);
  }
  i = o.slice(c, g).map(function(d, u) {
    var h = u + c + 1;
    return (h == n ? "  > " : "    ") + h + "| " + d;
  }).join(`
`), a.path = e;
  try {
    a.message = (e || "Pug") + ":" + n + `
` + i + `

` + a.message;
  } catch {
  }
  throw a;
}
function st(a) {
  var e = "", n, t;
  try {
    var i = a || {};
    (function(o) {
      t = 1, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + '<div class="g-config-breadcrumb-container"></div>', t = 2, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + '<form id="g-large-image-form" role="form">', t = 3, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + '<div class="form-group">', t = 4, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + "<label>", t = 4, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + "Store annotation history</label>", t = 5, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + '<p class="g-large-image-description">', t = 6, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + "Whenever annotations are saved, a record of the annotation's previous state can be kept.</p>", t = 7, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + '<div class="g-large-image-annotation-history-container">', t = 8, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + '<label class="radio-inline">', t = 9, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + "<input" + (' class="g-large-image-annotation-history-show" type="radio" name="g-large-image-annotation-history"' + $e("checked", o["large_image.annotation_history"] !== !1 ? "checked" : void 0, !0, !1)) + "/>", t = 10, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + "Record annotation history</label>", t = 11, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + '<label class="radio-inline">', t = 12, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + "<input" + (' class="g-large-image-annotation-history-hide" type="radio" name="g-large-image-annotation-history"' + $e("checked", o["large_image.annotation_history"] !== !1 ? void 0 : "checked", !0, !1)) + "/>", t = 13, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + "Don't store history</label></div></div>", t = 14, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + '<p class="g-validation-failed-message" id="g-large-image-error-message"></p>', t = 15, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/largeImageAnnotationConfig.pug", e = e + '<input class="btn btn-sm btn-primary" type="submit" value="Save"/></form>';
    }).call(this, "settings" in i ? i.settings : typeof settings < "u" ? settings : void 0);
  } catch (o) {
    Ve(o, n, t);
  }
  return e;
}
const ut = girder.views.View, lt = girder.views.widgets.PluginConfigBreadcrumbWidget, { restRequest: gt } = girder.rest, ct = girder.events;
var ie = ut.extend({
  events: {
    "submit #g-large-image-form": function(a) {
      a.preventDefault(), this.$("#g-large-image-error-message").empty(), this._saveSettings([{
        key: "large_image.annotation_history",
        value: this.$(".g-large-image-annotation-history-show").prop("checked")
      }]);
    }
  },
  initialize: function() {
    ie.getSettings((a) => {
      this.settings = a, this.render();
    });
  },
  render: function() {
    return this.$el.html(st({
      settings: this.settings,
      viewers: ie.viewers
    })), this.breadcrumb || (this.breadcrumb = new lt({
      pluginName: "Large image annotation",
      el: this.$(".g-config-breadcrumb-container"),
      parentView: this
    }).render()), this;
  },
  _saveSettings: function(a) {
    return gt({
      type: "PUT",
      url: "system/setting",
      data: {
        list: JSON.stringify(a)
      },
      error: null
    }).done(() => {
      ie.clearSettings(), ct.trigger("g:alert", {
        icon: "ok",
        text: "Settings saved.",
        type: "success",
        timeout: 4e3
      });
    }).fail((e) => {
      this.$("#g-large-image-error-message").text(
        e.responseJSON.message
      );
    });
  }
}, {
  /* Class methods and objects */
  /**
   * Get settings if we haven't yet done so.  Either way, call a callback
   * when we have settings.
   *
   * @param {function} callback a function to call after the settings are
   *      fetched.  If the settings are already present, this is called
   *      without any delay.
   */
  getSettings: function(a) {
    return girder.plugins.large_image.views.ConfigView.getSettings(a);
  },
  /**
   * Clear the settings so that getSettings will refetch them.
   */
  clearSettings: function() {
    return girder.plugins.large_image.views.ConfigView.clearSettings();
  }
});
const dt = girder.events, ht = girder.router, { exposePluginConfig: _t } = girder.utilities.PluginUtils;
_t("large_image_annotation", "plugins/large_image_annotation/config");
ht.route("plugins/large_image_annotation/config", "largeImageAnnotationConfig", function() {
  dt.trigger("g:navigateTo", ie);
});
function De(a, e, n, t) {
  if (!(a instanceof Error)) throw a;
  if (!(typeof window > "u" && e || t)) throw a.message += " on line " + n, a;
  var i, o, c, g;
  try {
    t = t || require("fs").readFileSync(e, { encoding: "utf8" }), i = 3, o = t.split(`
`), c = Math.max(n - i, 0), g = Math.min(o.length, n + i);
  } catch (d) {
    return a.message += " - could not read from " + e + " (" + d.message + ")", void De(a, null, n);
  }
  i = o.slice(c, g).map(function(d, u) {
    var h = u + c + 1;
    return (h == n ? "  > " : "    ") + h + "| " + d;
  }).join(`
`), a.path = e;
  try {
    a.message = (e || "Pug") + ":" + n + `
` + i + `

` + a.message;
  } catch {
  }
  throw a;
}
function Ft(a) {
  var e = "", n, t;
  try {
    t = 1, n = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/imageViewerAnnotationList.pug", e = e + '<div class="g-annotation-list-container"></div>';
  } catch (i) {
    De(i, n, t);
  }
  return e;
}
const pt = girder.Backbone, ft = pt.Model.extend({
  idAttribute: "id"
}), mt = girder.Backbone, Ne = mt.Collection.extend({
  model: ft,
  comparator: void 0
});
function Le(a, e) {
  const n = Math.cos(a), t = Math.sin(a);
  return e = e || [0, 0], function(i) {
    const o = i[0] - e[0], c = i[1] - e[1];
    return [
      o * n - c * t + e[0],
      o * t + c * n + e[1]
    ];
  };
}
const yt = girder._;
function bt(a) {
  const e = a.center, n = e[0], t = e[1], i = a.height, o = a.width, c = a.rotation || 0, g = n - o / 2, d = n + o / 2, u = t - i / 2, h = t + i / 2;
  return {
    type: "Polygon",
    coordinates: [yt.map([
      [g, u],
      [d, u],
      [d, h],
      [g, h],
      [g, u]
    ], Le(c, e))],
    annotationType: "rectangle"
  };
}
const wt = girder._;
function vt(a) {
  const e = a.center, n = e[0], t = e[1], i = a.height, o = a.width, c = a.rotation || 0, g = n - o / 2, d = n + o / 2, u = t - i / 2, h = t + i / 2;
  return {
    type: "Polygon",
    coordinates: [wt.map([
      [g, u],
      [d, u],
      [d, h],
      [g, h],
      [g, u]
    ], Le(c, e))],
    annotationType: "ellipse"
  };
}
function Ct(a) {
  const e = a.center, n = e[0], t = e[1], i = a.radius, o = n - i, c = n + i, g = t - i, d = t + i;
  return {
    type: "Polygon",
    coordinates: [[
      [o, g],
      [c, g],
      [c, d],
      [o, d],
      [o, g]
    ]],
    annotationType: "circle"
  };
}
const me = girder._;
function Lt(a) {
  const e = me.map(a.points, (o) => me.first(o, 2));
  var n, t, i;
  if (a.closed) {
    if (e.push(e[0]), t = [e], a.holes) {
      const o = (a.holes || []).map((c) => {
        const g = c.map((d) => me.first(d, 2));
        return g.push(g[0]), g;
      });
      t = t.concat(o);
    }
    n = "Polygon", i = "polygon";
  } else
    n = "LineString", t = e, i = "line";
  return {
    type: n,
    coordinates: t,
    annotationType: i
  };
}
const At = girder._;
function Et(a) {
  return {
    type: "Point",
    coordinates: At.first(a.center, 2),
    annotationType: "point"
  };
}
const ve = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  circle: Ct,
  ellipse: vt,
  point: Et,
  polyline: Lt,
  rectangle: bt
}, Symbol.toStringTag, { value: "Module" })), xt = {
  fillColor: "rgba(0,0,0,0)",
  lineColor: "rgb(0,0,0)",
  lineWidth: 2,
  rotation: 0,
  normal: [0, 0, 1]
}, jt = {
  fillColor: "rgba(0,0,0,0)",
  lineColor: "rgb(0,0,0)",
  lineWidth: 2,
  rotation: 0,
  normal: [0, 0, 1]
}, Wt = {
  fillColor: "rgba(0,0,0,0)",
  lineColor: "rgb(0,0,0)",
  lineWidth: 2
}, Ot = {
  fillColor: "rgba(0,0,0,0)",
  lineColor: "rgb(0,0,0)",
  lineWidth: 2
}, $t = {
  lineColor: "rgb(0,0,0)",
  lineWidth: 2,
  fillColor: "rgba(0,0,0,0)"
}, Ae = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  circle: Wt,
  ellipse: jt,
  point: $t,
  polyline: Ot,
  rectangle: xt
}, Symbol.toStringTag, { value: "Module" }));
function St(a) {
  return a && a.__esModule && Object.prototype.hasOwnProperty.call(a, "default") ? a.default : a;
}
var Be = { exports: {} };
(function(a) {
  (function(e) {
    var n = /^\s+/, t = /\s+$/, i = 0, o = e.round, c = e.min, g = e.max, d = e.random;
    function u(r, l) {
      if (r = r || "", l = l || {}, r instanceof u)
        return r;
      if (!(this instanceof u))
        return new u(r, l);
      var s = h(r);
      this._originalInput = r, this._r = s.r, this._g = s.g, this._b = s.b, this._a = s.a, this._roundA = o(100 * this._a) / 100, this._format = l.format || s.format, this._gradientType = l.gradientType, this._r < 1 && (this._r = o(this._r)), this._g < 1 && (this._g = o(this._g)), this._b < 1 && (this._b = o(this._b)), this._ok = s.ok, this._tc_id = i++;
    }
    u.prototype = {
      isDark: function() {
        return this.getBrightness() < 128;
      },
      isLight: function() {
        return !this.isDark();
      },
      isValid: function() {
        return this._ok;
      },
      getOriginalInput: function() {
        return this._originalInput;
      },
      getFormat: function() {
        return this._format;
      },
      getAlpha: function() {
        return this._a;
      },
      getBrightness: function() {
        var r = this.toRgb();
        return (r.r * 299 + r.g * 587 + r.b * 114) / 1e3;
      },
      getLuminance: function() {
        var r = this.toRgb(), l, s, _, f, p, j;
        return l = r.r / 255, s = r.g / 255, _ = r.b / 255, l <= 0.03928 ? f = l / 12.92 : f = e.pow((l + 0.055) / 1.055, 2.4), s <= 0.03928 ? p = s / 12.92 : p = e.pow((s + 0.055) / 1.055, 2.4), _ <= 0.03928 ? j = _ / 12.92 : j = e.pow((_ + 0.055) / 1.055, 2.4), 0.2126 * f + 0.7152 * p + 0.0722 * j;
      },
      setAlpha: function(r) {
        return this._a = B(r), this._roundA = o(100 * this._a) / 100, this;
      },
      toHsv: function() {
        var r = v(this._r, this._g, this._b);
        return { h: r.h * 360, s: r.s, v: r.v, a: this._a };
      },
      toHsvString: function() {
        var r = v(this._r, this._g, this._b), l = o(r.h * 360), s = o(r.s * 100), _ = o(r.v * 100);
        return this._a == 1 ? "hsv(" + l + ", " + s + "%, " + _ + "%)" : "hsva(" + l + ", " + s + "%, " + _ + "%, " + this._roundA + ")";
      },
      toHsl: function() {
        var r = y(this._r, this._g, this._b);
        return { h: r.h * 360, s: r.s, l: r.l, a: this._a };
      },
      toHslString: function() {
        var r = y(this._r, this._g, this._b), l = o(r.h * 360), s = o(r.s * 100), _ = o(r.l * 100);
        return this._a == 1 ? "hsl(" + l + ", " + s + "%, " + _ + "%)" : "hsla(" + l + ", " + s + "%, " + _ + "%, " + this._roundA + ")";
      },
      toHex: function(r) {
        return T(this._r, this._g, this._b, r);
      },
      toHexString: function(r) {
        return "#" + this.toHex(r);
      },
      toHex8: function(r) {
        return M(this._r, this._g, this._b, this._a, r);
      },
      toHex8String: function(r) {
        return "#" + this.toHex8(r);
      },
      toRgb: function() {
        return { r: o(this._r), g: o(this._g), b: o(this._b), a: this._a };
      },
      toRgbString: function() {
        return this._a == 1 ? "rgb(" + o(this._r) + ", " + o(this._g) + ", " + o(this._b) + ")" : "rgba(" + o(this._r) + ", " + o(this._g) + ", " + o(this._b) + ", " + this._roundA + ")";
      },
      toPercentageRgb: function() {
        return { r: o(A(this._r, 255) * 100) + "%", g: o(A(this._g, 255) * 100) + "%", b: o(A(this._b, 255) * 100) + "%", a: this._a };
      },
      toPercentageRgbString: function() {
        return this._a == 1 ? "rgb(" + o(A(this._r, 255) * 100) + "%, " + o(A(this._g, 255) * 100) + "%, " + o(A(this._b, 255) * 100) + "%)" : "rgba(" + o(A(this._r, 255) * 100) + "%, " + o(A(this._g, 255) * 100) + "%, " + o(A(this._b, 255) * 100) + "%, " + this._roundA + ")";
      },
      toName: function() {
        return this._a === 0 ? "transparent" : this._a < 1 ? !1 : tt[T(this._r, this._g, this._b, !0)] || !1;
      },
      toFilter: function(r) {
        var l = "#" + W(this._r, this._g, this._b, this._a), s = l, _ = this._gradientType ? "GradientType = 1, " : "";
        if (r) {
          var f = u(r);
          s = "#" + W(f._r, f._g, f._b, f._a);
        }
        return "progid:DXImageTransform.Microsoft.gradient(" + _ + "startColorstr=" + l + ",endColorstr=" + s + ")";
      },
      toString: function(r) {
        var l = !!r;
        r = r || this._format;
        var s = !1, _ = this._a < 1 && this._a >= 0, f = !l && _ && (r === "hex" || r === "hex6" || r === "hex3" || r === "hex4" || r === "hex8" || r === "name");
        return f ? r === "name" && this._a === 0 ? this.toName() : this.toRgbString() : (r === "rgb" && (s = this.toRgbString()), r === "prgb" && (s = this.toPercentageRgbString()), (r === "hex" || r === "hex6") && (s = this.toHexString()), r === "hex3" && (s = this.toHexString(!0)), r === "hex4" && (s = this.toHex8String(!0)), r === "hex8" && (s = this.toHex8String()), r === "name" && (s = this.toName()), r === "hsl" && (s = this.toHslString()), r === "hsv" && (s = this.toHsvString()), s || this.toHexString());
      },
      clone: function() {
        return u(this.toString());
      },
      _applyModification: function(r, l) {
        var s = r.apply(null, [this].concat([].slice.call(l)));
        return this._r = s._r, this._g = s._g, this._b = s._b, this.setAlpha(s._a), this;
      },
      lighten: function() {
        return this._applyModification(ae, arguments);
      },
      brighten: function() {
        return this._applyModification(Z, arguments);
      },
      darken: function() {
        return this._applyModification(z, arguments);
      },
      desaturate: function() {
        return this._applyModification(I, arguments);
      },
      saturate: function() {
        return this._applyModification(D, arguments);
      },
      greyscale: function() {
        return this._applyModification(m, arguments);
      },
      spin: function() {
        return this._applyModification(Q, arguments);
      },
      _applyCombination: function(r, l) {
        return r.apply(null, [this].concat([].slice.call(l)));
      },
      analogous: function() {
        return this._applyCombination(C, arguments);
      },
      complement: function() {
        return this._applyCombination(J, arguments);
      },
      monochromatic: function() {
        return this._applyCombination(E, arguments);
      },
      splitcomplement: function() {
        return this._applyCombination(re, arguments);
      },
      triad: function() {
        return this._applyCombination(Y, arguments);
      },
      tetrad: function() {
        return this._applyCombination(X, arguments);
      }
    }, u.fromRatio = function(r, l) {
      if (typeof r == "object") {
        var s = {};
        for (var _ in r)
          r.hasOwnProperty(_) && (_ === "a" ? s[_] = r[_] : s[_] = se(r[_]));
        r = s;
      }
      return u(r, l);
    };
    function h(r) {
      var l = { r: 0, g: 0, b: 0 }, s = 1, _ = null, f = null, p = null, j = !1, S = !1;
      return typeof r == "string" && (r = it(r)), typeof r == "object" && (N(r.r) && N(r.g) && N(r.b) ? (l = F(r.r, r.g, r.b), j = !0, S = String(r.r).substr(-1) === "%" ? "prgb" : "rgb") : N(r.h) && N(r.s) && N(r.v) ? (_ = se(r.s), f = se(r.v), l = L(r.h, _, f), j = !0, S = "hsv") : N(r.h) && N(r.s) && N(r.l) && (_ = se(r.s), p = se(r.l), l = b(r.h, _, p), j = !0, S = "hsl"), r.hasOwnProperty("a") && (s = r.a)), s = B(s), {
        ok: j,
        format: r.format || S,
        r: c(255, g(l.r, 0)),
        g: c(255, g(l.g, 0)),
        b: c(255, g(l.b, 0)),
        a: s
      };
    }
    function F(r, l, s) {
      return {
        r: A(r, 255) * 255,
        g: A(l, 255) * 255,
        b: A(s, 255) * 255
      };
    }
    function y(r, l, s) {
      r = A(r, 255), l = A(l, 255), s = A(s, 255);
      var _ = g(r, l, s), f = c(r, l, s), p, j, S = (_ + f) / 2;
      if (_ == f)
        p = j = 0;
      else {
        var k = _ - f;
        switch (j = S > 0.5 ? k / (2 - _ - f) : k / (_ + f), _) {
          case r:
            p = (l - s) / k + (l < s ? 6 : 0);
            break;
          case l:
            p = (s - r) / k + 2;
            break;
          case s:
            p = (r - l) / k + 4;
            break;
        }
        p /= 6;
      }
      return { h: p, s: j, l: S };
    }
    function b(r, l, s) {
      var _, f, p;
      r = A(r, 360), l = A(l, 100), s = A(s, 100);
      function j(P, ue, V) {
        return V < 0 && (V += 1), V > 1 && (V -= 1), V < 1 / 6 ? P + (ue - P) * 6 * V : V < 1 / 2 ? ue : V < 2 / 3 ? P + (ue - P) * (2 / 3 - V) * 6 : P;
      }
      if (l === 0)
        _ = f = p = s;
      else {
        var S = s < 0.5 ? s * (1 + l) : s + l - s * l, k = 2 * s - S;
        _ = j(k, S, r + 1 / 3), f = j(k, S, r), p = j(k, S, r - 1 / 3);
      }
      return { r: _ * 255, g: f * 255, b: p * 255 };
    }
    function v(r, l, s) {
      r = A(r, 255), l = A(l, 255), s = A(s, 255);
      var _ = g(r, l, s), f = c(r, l, s), p, j, S = _, k = _ - f;
      if (j = _ === 0 ? 0 : k / _, _ == f)
        p = 0;
      else {
        switch (_) {
          case r:
            p = (l - s) / k + (l < s ? 6 : 0);
            break;
          case l:
            p = (s - r) / k + 2;
            break;
          case s:
            p = (r - l) / k + 4;
            break;
        }
        p /= 6;
      }
      return { h: p, s: j, v: S };
    }
    function L(r, l, s) {
      r = A(r, 360) * 6, l = A(l, 100), s = A(s, 100);
      var _ = e.floor(r), f = r - _, p = s * (1 - l), j = s * (1 - f * l), S = s * (1 - (1 - f) * l), k = _ % 6, P = [s, j, p, p, S, s][k], ue = [S, s, s, j, p, p][k], V = [p, p, S, s, s, j][k];
      return { r: P * 255, g: ue * 255, b: V * 255 };
    }
    function T(r, l, s, _) {
      var f = [
        H(o(r).toString(16)),
        H(o(l).toString(16)),
        H(o(s).toString(16))
      ];
      return _ && f[0].charAt(0) == f[0].charAt(1) && f[1].charAt(0) == f[1].charAt(1) && f[2].charAt(0) == f[2].charAt(1) ? f[0].charAt(0) + f[1].charAt(0) + f[2].charAt(0) : f.join("");
    }
    function M(r, l, s, _, f) {
      var p = [
        H(o(r).toString(16)),
        H(o(l).toString(16)),
        H(o(s).toString(16)),
        H(Oe(_))
      ];
      return f && p[0].charAt(0) == p[0].charAt(1) && p[1].charAt(0) == p[1].charAt(1) && p[2].charAt(0) == p[2].charAt(1) && p[3].charAt(0) == p[3].charAt(1) ? p[0].charAt(0) + p[1].charAt(0) + p[2].charAt(0) + p[3].charAt(0) : p.join("");
    }
    function W(r, l, s, _) {
      var f = [
        H(Oe(_)),
        H(o(r).toString(16)),
        H(o(l).toString(16)),
        H(o(s).toString(16))
      ];
      return f.join("");
    }
    u.equals = function(r, l) {
      return !r || !l ? !1 : u(r).toRgbString() == u(l).toRgbString();
    }, u.random = function() {
      return u.fromRatio({
        r: d(),
        g: d(),
        b: d()
      });
    };
    function I(r, l) {
      l = l === 0 ? 0 : l || 10;
      var s = u(r).toHsl();
      return s.s -= l / 100, s.s = q(s.s), u(s);
    }
    function D(r, l) {
      l = l === 0 ? 0 : l || 10;
      var s = u(r).toHsl();
      return s.s += l / 100, s.s = q(s.s), u(s);
    }
    function m(r) {
      return u(r).desaturate(100);
    }
    function ae(r, l) {
      l = l === 0 ? 0 : l || 10;
      var s = u(r).toHsl();
      return s.l += l / 100, s.l = q(s.l), u(s);
    }
    function Z(r, l) {
      l = l === 0 ? 0 : l || 10;
      var s = u(r).toRgb();
      return s.r = g(0, c(255, s.r - o(255 * -(l / 100)))), s.g = g(0, c(255, s.g - o(255 * -(l / 100)))), s.b = g(0, c(255, s.b - o(255 * -(l / 100)))), u(s);
    }
    function z(r, l) {
      l = l === 0 ? 0 : l || 10;
      var s = u(r).toHsl();
      return s.l -= l / 100, s.l = q(s.l), u(s);
    }
    function Q(r, l) {
      var s = u(r).toHsl(), _ = (s.h + l) % 360;
      return s.h = _ < 0 ? 360 + _ : _, u(s);
    }
    function J(r) {
      var l = u(r).toHsl();
      return l.h = (l.h + 180) % 360, u(l);
    }
    function Y(r) {
      var l = u(r).toHsl(), s = l.h;
      return [
        u(r),
        u({ h: (s + 120) % 360, s: l.s, l: l.l }),
        u({ h: (s + 240) % 360, s: l.s, l: l.l })
      ];
    }
    function X(r) {
      var l = u(r).toHsl(), s = l.h;
      return [
        u(r),
        u({ h: (s + 90) % 360, s: l.s, l: l.l }),
        u({ h: (s + 180) % 360, s: l.s, l: l.l }),
        u({ h: (s + 270) % 360, s: l.s, l: l.l })
      ];
    }
    function re(r) {
      var l = u(r).toHsl(), s = l.h;
      return [
        u(r),
        u({ h: (s + 72) % 360, s: l.s, l: l.l }),
        u({ h: (s + 216) % 360, s: l.s, l: l.l })
      ];
    }
    function C(r, l, s) {
      l = l || 6, s = s || 30;
      var _ = u(r).toHsl(), f = 360 / s, p = [u(r)];
      for (_.h = (_.h - (f * l >> 1) + 720) % 360; --l; )
        _.h = (_.h + f) % 360, p.push(u(_));
      return p;
    }
    function E(r, l) {
      l = l || 6;
      for (var s = u(r).toHsv(), _ = s.h, f = s.s, p = s.v, j = [], S = 1 / l; l--; )
        j.push(u({ h: _, s: f, v: p })), p = (p + S) % 1;
      return j;
    }
    u.mix = function(r, l, s) {
      s = s === 0 ? 0 : s || 50;
      var _ = u(r).toRgb(), f = u(l).toRgb(), p = s / 100, j = {
        r: (f.r - _.r) * p + _.r,
        g: (f.g - _.g) * p + _.g,
        b: (f.b - _.b) * p + _.b,
        a: (f.a - _.a) * p + _.a
      };
      return u(j);
    }, u.readability = function(r, l) {
      var s = u(r), _ = u(l);
      return (e.max(s.getLuminance(), _.getLuminance()) + 0.05) / (e.min(s.getLuminance(), _.getLuminance()) + 0.05);
    }, u.isReadable = function(r, l, s) {
      var _ = u.readability(r, l), f, p;
      switch (p = !1, f = at(s), f.level + f.size) {
        case "AAsmall":
        case "AAAlarge":
          p = _ >= 4.5;
          break;
        case "AAlarge":
          p = _ >= 3;
          break;
        case "AAAsmall":
          p = _ >= 7;
          break;
      }
      return p;
    }, u.mostReadable = function(r, l, s) {
      var _ = null, f = 0, p, j, S, k;
      s = s || {}, j = s.includeFallbackColors, S = s.level, k = s.size;
      for (var P = 0; P < l.length; P++)
        p = u.readability(r, l[P]), p > f && (f = p, _ = u(l[P]));
      return u.isReadable(r, _, { level: S, size: k }) || !j ? _ : (s.includeFallbackColors = !1, u.mostReadable(r, ["#fff", "#000"], s));
    };
    var oe = u.names = {
      aliceblue: "f0f8ff",
      antiquewhite: "faebd7",
      aqua: "0ff",
      aquamarine: "7fffd4",
      azure: "f0ffff",
      beige: "f5f5dc",
      bisque: "ffe4c4",
      black: "000",
      blanchedalmond: "ffebcd",
      blue: "00f",
      blueviolet: "8a2be2",
      brown: "a52a2a",
      burlywood: "deb887",
      burntsienna: "ea7e5d",
      cadetblue: "5f9ea0",
      chartreuse: "7fff00",
      chocolate: "d2691e",
      coral: "ff7f50",
      cornflowerblue: "6495ed",
      cornsilk: "fff8dc",
      crimson: "dc143c",
      cyan: "0ff",
      darkblue: "00008b",
      darkcyan: "008b8b",
      darkgoldenrod: "b8860b",
      darkgray: "a9a9a9",
      darkgreen: "006400",
      darkgrey: "a9a9a9",
      darkkhaki: "bdb76b",
      darkmagenta: "8b008b",
      darkolivegreen: "556b2f",
      darkorange: "ff8c00",
      darkorchid: "9932cc",
      darkred: "8b0000",
      darksalmon: "e9967a",
      darkseagreen: "8fbc8f",
      darkslateblue: "483d8b",
      darkslategray: "2f4f4f",
      darkslategrey: "2f4f4f",
      darkturquoise: "00ced1",
      darkviolet: "9400d3",
      deeppink: "ff1493",
      deepskyblue: "00bfff",
      dimgray: "696969",
      dimgrey: "696969",
      dodgerblue: "1e90ff",
      firebrick: "b22222",
      floralwhite: "fffaf0",
      forestgreen: "228b22",
      fuchsia: "f0f",
      gainsboro: "dcdcdc",
      ghostwhite: "f8f8ff",
      gold: "ffd700",
      goldenrod: "daa520",
      gray: "808080",
      green: "008000",
      greenyellow: "adff2f",
      grey: "808080",
      honeydew: "f0fff0",
      hotpink: "ff69b4",
      indianred: "cd5c5c",
      indigo: "4b0082",
      ivory: "fffff0",
      khaki: "f0e68c",
      lavender: "e6e6fa",
      lavenderblush: "fff0f5",
      lawngreen: "7cfc00",
      lemonchiffon: "fffacd",
      lightblue: "add8e6",
      lightcoral: "f08080",
      lightcyan: "e0ffff",
      lightgoldenrodyellow: "fafad2",
      lightgray: "d3d3d3",
      lightgreen: "90ee90",
      lightgrey: "d3d3d3",
      lightpink: "ffb6c1",
      lightsalmon: "ffa07a",
      lightseagreen: "20b2aa",
      lightskyblue: "87cefa",
      lightslategray: "789",
      lightslategrey: "789",
      lightsteelblue: "b0c4de",
      lightyellow: "ffffe0",
      lime: "0f0",
      limegreen: "32cd32",
      linen: "faf0e6",
      magenta: "f0f",
      maroon: "800000",
      mediumaquamarine: "66cdaa",
      mediumblue: "0000cd",
      mediumorchid: "ba55d3",
      mediumpurple: "9370db",
      mediumseagreen: "3cb371",
      mediumslateblue: "7b68ee",
      mediumspringgreen: "00fa9a",
      mediumturquoise: "48d1cc",
      mediumvioletred: "c71585",
      midnightblue: "191970",
      mintcream: "f5fffa",
      mistyrose: "ffe4e1",
      moccasin: "ffe4b5",
      navajowhite: "ffdead",
      navy: "000080",
      oldlace: "fdf5e6",
      olive: "808000",
      olivedrab: "6b8e23",
      orange: "ffa500",
      orangered: "ff4500",
      orchid: "da70d6",
      palegoldenrod: "eee8aa",
      palegreen: "98fb98",
      paleturquoise: "afeeee",
      palevioletred: "db7093",
      papayawhip: "ffefd5",
      peachpuff: "ffdab9",
      peru: "cd853f",
      pink: "ffc0cb",
      plum: "dda0dd",
      powderblue: "b0e0e6",
      purple: "800080",
      rebeccapurple: "663399",
      red: "f00",
      rosybrown: "bc8f8f",
      royalblue: "4169e1",
      saddlebrown: "8b4513",
      salmon: "fa8072",
      sandybrown: "f4a460",
      seagreen: "2e8b57",
      seashell: "fff5ee",
      sienna: "a0522d",
      silver: "c0c0c0",
      skyblue: "87ceeb",
      slateblue: "6a5acd",
      slategray: "708090",
      slategrey: "708090",
      snow: "fffafa",
      springgreen: "00ff7f",
      steelblue: "4682b4",
      tan: "d2b48c",
      teal: "008080",
      thistle: "d8bfd8",
      tomato: "ff6347",
      turquoise: "40e0d0",
      violet: "ee82ee",
      wheat: "f5deb3",
      white: "fff",
      whitesmoke: "f5f5f5",
      yellow: "ff0",
      yellowgreen: "9acd32"
    }, tt = u.hexNames = nt(oe);
    function nt(r) {
      var l = {};
      for (var s in r)
        r.hasOwnProperty(s) && (l[r[s]] = s);
      return l;
    }
    function B(r) {
      return r = parseFloat(r), (isNaN(r) || r < 0 || r > 1) && (r = 1), r;
    }
    function A(r, l) {
      x(r) && (r = "100%");
      var s = fe(r);
      return r = c(l, g(0, parseFloat(r))), s && (r = parseInt(r * l, 10) / 100), e.abs(r - l) < 1e-6 ? 1 : r % l / parseFloat(l);
    }
    function q(r) {
      return c(1, g(0, r));
    }
    function w(r) {
      return parseInt(r, 16);
    }
    function x(r) {
      return typeof r == "string" && r.indexOf(".") != -1 && parseFloat(r) === 1;
    }
    function fe(r) {
      return typeof r == "string" && r.indexOf("%") != -1;
    }
    function H(r) {
      return r.length == 1 ? "0" + r : "" + r;
    }
    function se(r) {
      return r <= 1 && (r = r * 100 + "%"), r;
    }
    function Oe(r) {
      return e.round(parseFloat(r) * 255).toString(16);
    }
    function ce(r) {
      return w(r) / 255;
    }
    var U = function() {
      var r = "[-\\+]?\\d+%?", l = "[-\\+]?\\d*\\.\\d+%?", s = "(?:" + l + ")|(?:" + r + ")", _ = "[\\s|\\(]+(" + s + ")[,|\\s]+(" + s + ")[,|\\s]+(" + s + ")\\s*\\)?", f = "[\\s|\\(]+(" + s + ")[,|\\s]+(" + s + ")[,|\\s]+(" + s + ")[,|\\s]+(" + s + ")\\s*\\)?";
      return {
        CSS_UNIT: new RegExp(s),
        rgb: new RegExp("rgb" + _),
        rgba: new RegExp("rgba" + f),
        hsl: new RegExp("hsl" + _),
        hsla: new RegExp("hsla" + f),
        hsv: new RegExp("hsv" + _),
        hsva: new RegExp("hsva" + f),
        hex3: /^#?([0-9a-fA-F]{1})([0-9a-fA-F]{1})([0-9a-fA-F]{1})$/,
        hex6: /^#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$/,
        hex4: /^#?([0-9a-fA-F]{1})([0-9a-fA-F]{1})([0-9a-fA-F]{1})([0-9a-fA-F]{1})$/,
        hex8: /^#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$/
      };
    }();
    function N(r) {
      return !!U.CSS_UNIT.exec(r);
    }
    function it(r) {
      r = r.replace(n, "").replace(t, "").toLowerCase();
      var l = !1;
      if (oe[r])
        r = oe[r], l = !0;
      else if (r == "transparent")
        return { r: 0, g: 0, b: 0, a: 0, format: "name" };
      var s;
      return (s = U.rgb.exec(r)) ? { r: s[1], g: s[2], b: s[3] } : (s = U.rgba.exec(r)) ? { r: s[1], g: s[2], b: s[3], a: s[4] } : (s = U.hsl.exec(r)) ? { h: s[1], s: s[2], l: s[3] } : (s = U.hsla.exec(r)) ? { h: s[1], s: s[2], l: s[3], a: s[4] } : (s = U.hsv.exec(r)) ? { h: s[1], s: s[2], v: s[3] } : (s = U.hsva.exec(r)) ? { h: s[1], s: s[2], v: s[3], a: s[4] } : (s = U.hex8.exec(r)) ? {
        r: w(s[1]),
        g: w(s[2]),
        b: w(s[3]),
        a: ce(s[4]),
        format: l ? "name" : "hex8"
      } : (s = U.hex6.exec(r)) ? {
        r: w(s[1]),
        g: w(s[2]),
        b: w(s[3]),
        format: l ? "name" : "hex"
      } : (s = U.hex4.exec(r)) ? {
        r: w(s[1] + "" + s[1]),
        g: w(s[2] + "" + s[2]),
        b: w(s[3] + "" + s[3]),
        a: ce(s[4] + "" + s[4]),
        format: l ? "name" : "hex8"
      } : (s = U.hex3.exec(r)) ? {
        r: w(s[1] + "" + s[1]),
        g: w(s[2] + "" + s[2]),
        b: w(s[3] + "" + s[3]),
        format: l ? "name" : "hex"
      } : !1;
    }
    function at(r) {
      var l, s;
      return r = r || { level: "AA", size: "small" }, l = (r.level || "AA").toUpperCase(), s = (r.size || "small").toLowerCase(), l !== "AA" && l !== "AAA" && (l = "AA"), s !== "small" && s !== "large" && (s = "small"), { level: l, size: s };
    }
    a.exports ? a.exports = u : window.tinycolor = u;
  })(Math);
})(Be);
var kt = Be.exports;
const Tt = /* @__PURE__ */ St(kt);
var K = { entries: 0 };
function Se(a) {
  if (K[a])
    return K[a];
  var e = Tt(a), n = {
    rgb: e.toHexString(),
    alpha: e.getAlpha()
  };
  return K.entries += 1, K.entries > 100 && (K = { entries: 0 }), K[a] = n, n;
}
function Ee(a) {
  var e;
  const n = {};
  return a.label && (n.label = a.label), a.fillColor && (e = Se(a.fillColor), n.fillColor = e.rgb, n.fillOpacity = e.alpha), a.lineColor && (e = Se(a.lineColor), n.strokeColor = e.rgb, n.strokeOpacity = e.alpha), a.lineWidth && (n.strokeWidth = a.lineWidth), n;
}
const _e = girder._;
function It(a) {
  return function(e, n) {
    if (("" + n).startsWith("_"))
      return;
    const t = e.type;
    if (e = _e.defaults({}, e, Ae[t] || {}), !_e.has(ve, t))
      return;
    const i = ve[t](e);
    return {
      type: "Feature",
      id: e.id,
      geometry: { type: i.type, coordinates: i.coordinates },
      properties: _e.extend({ element: e, annotationType: i.annotationType }, a, Ee(e))
    };
  };
}
function qe(a, e = {}) {
  return {
    type: "FeatureCollection",
    features: _e.chain(a).mapObject(It(e)).compact().value()
  };
}
function xe(a, e) {
  let n = 0, t = 1, i = 0, o = null;
  const c = {
    0: { r: 0, g: 0, b: 0, a: 0 },
    1: { r: 1, g: 1, b: 0, a: 1 }
  };
  if (a.colorRange && a.rangeValues) {
    if (a.normalizeRange || !e.length)
      for (let g = 0; g < a.colorRange.length && g < a.rangeValues.length; g += 1) {
        const d = Math.max(0, Math.min(1, a.rangeValues[g]));
        if (c[d] = a.colorRange[g], d >= 1)
          break;
      }
    else if (a.colorRange.length >= 2 && a.rangeValues.length >= 2) {
      n = t = a.rangeValues[0] || 0;
      for (let g = 1; g < a.rangeValues.length; g += 1) {
        const d = a.rangeValues[g] || 0;
        d < n && (n = d), d > t && (t = d);
      }
      n === t && (n -= 1), i = void 0;
      for (let g = 0; g < a.colorRange.length && g < a.rangeValues.length; g += 1) {
        let d = (a.rangeValues[g] - n) / (t - n || 1);
        if ((d <= 0 || i === void 0) && (i = a.rangeValues[g]), o = a.rangeValues[g], d = Math.max(0, Math.min(1, d)), c[d] = a.colorRange[g], d >= 1)
          break;
      }
    }
  }
  return {
    color: c,
    min: i,
    max: o
  };
}
function Rt(a, e, n) {
  const t = n.map(), i = t.layers().find((u) => u instanceof window.geo.tileLayer && u.options && u.options.maxLevel !== void 0), o = i ? 2 ** -i.options.maxLevel : 1, c = t.createLayer("feature", { features: ["heatmap"] }), g = xe(a, a.points.map((u) => u[3])), d = c.createFeature("heatmap", {
    style: {
      radius: (a.radius || 25) * (a.scaleWithZoom ? o : 1),
      blurRadius: 0,
      gaussian: !0,
      color: g.color,
      scaleWithZoom: a.scaleWithZoom || !1
    },
    position: (u) => ({ x: u[0], y: u[1], z: u[2] }),
    intensity: (u) => u[3] || 0,
    minIntensity: g.min,
    maxIntensity: g.max,
    updateDelay: 100
  }).data(a.points);
  return d._ownLayer = !0, [d];
}
function Mt(a, e, n) {
  const t = n.map(), i = t.createLayer("feature", { features: ["heatmap"] }), o = (a.origin || [0, 0, 0])[0] || 0, c = (a.origin || [0, 0, 0])[1] || 0, g = (a.origin || [0, 0, 0])[2] || 0, d = a.dx || 1, u = a.dy || 1, h = xe(a, a.values), F = t.layers().find((v) => v instanceof window.geo.tileLayer && v.options && v.options.maxLevel !== void 0), y = F ? 2 ** -F.options.maxLevel : 1, b = i.createFeature("heatmap", {
    style: {
      radius: (a.radius || 25) * (a.scaleWithZoom ? y : 1),
      blurRadius: 0,
      gaussian: !0,
      color: h.color,
      scaleWithZoom: a.scaleWithZoom || !1
    },
    position: (v, L) => ({
      x: o + d * (L % a.gridWidth),
      y: c + u * Math.floor(L / a.gridWidth),
      z: g
    }),
    intensity: (v) => v || 0,
    minIntensity: h.min,
    maxIntensity: h.max,
    updateDelay: 100
  }).data(a.values);
  return b._ownLayer = !0, [b];
}
function Pt(a, e, n) {
  let t = a.values[0] || 0, i = t;
  for (let c = 1; c < a.values.length; c += 1)
    a.values[c] > i && (i = a.values[c]), a.values[c] < i && (t = a.values[c]);
  return t >= 0 && (t = -1), [n.createFeature("contour", {
    style: {
      value: (c) => c || 0
    },
    contour: {
      gridWidth: a.gridWidth,
      x0: (a.origin || [])[0] || 0,
      y0: (a.origin || [])[1] || 0,
      dx: a.dx || 1,
      dy: a.dy || 1,
      stepped: !1,
      colorRange: [
        a.minColor || { r: 0, g: 0, b: 1, a: 1 },
        a.zeroColor || { r: 0, g: 0, b: 0, a: 0 },
        a.maxColor || { r: 1, g: 1, b: 0, a: 1 }
      ],
      rangeValues: [t, 0, Math.max(0, i)]
    }
  }).data(a.values)];
}
const ke = {
  griddata_contour: Pt,
  griddata_heatmap: Mt,
  heatmap: Rt
};
function Ge(a, e = {}, n) {
  try {
    var t = [];
    return a.forEach((i) => {
      const o = ke[i.type + "_" + i.interpretation] || ke[i.type];
      o && (t = t.concat(o(i, e, n)));
    }), t;
  } catch (i) {
    console.error(i);
  }
}
const zt = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  convertFeatures: Ge,
  heatmapColorTable: xe
}, Symbol.toStringTag, { value: "Module" })), ne = girder._, Ht = girder.models.AccessControlledModel, { getCurrentUser: ee } = girder.auth, { restRequest: de } = girder.rest, Ut = girder.models.MetadataMixin, le = Ht.extend({
  resourceName: "annotation",
  defaults: {
    annotation: {},
    minElements: 5e3,
    maxDetails: 25e4,
    maxCentroids: 2e6
  },
  initialize() {
    !this.get("updated") && ee() && (this.attributes.updated = "" + Date.now(), this.attributes.updatedId = ee().id), this._region = {
      maxDetails: this.get("maxDetails"),
      minElements: this.get("minElements"),
      sort: "size",
      sortdir: -1
    }, this._viewArea = 3, this._elements = new Ne(
      this.get("annotation").elements || []
    ), this._elements.annotation = this, this.listenTo(this._elements, "change add remove reset", () => {
      var a = ne.extend({}, this.get("annotation"));
      a.elements = this._elements.toJSON(), this.set("annotation", a);
    });
  },
  /**
   * Fetch the centroids and unpack the binary data.
   */
  fetchCentroids: function() {
    var a = (this.altUrl || this.resourceName) + "/" + this.get("_id"), e = {
      url: a,
      data: {
        sort: "size",
        sortdir: -1,
        centroids: !0,
        limit: this.get("maxCentroids"),
        _: (this.get("updated") || this.get("created")) + "_" + this.get("_version")
      },
      xhrFields: {
        responseType: "arraybuffer"
      },
      error: null
    };
    return de(e).done((n) => {
      let t = new DataView(n), i = 0, o = t.byteLength - 1;
      for (; t.getUint8(i) && i < t.byteLength; i += 1) ;
      for (; t.getUint8(o) && o >= 0; o -= 1) ;
      if (i >= o)
        throw new Error("invalid centroid data");
      const c = new Uint8Array(i + t.byteLength - o - 1);
      c.set(new Uint8Array(n.slice(0, i)), 0), c.set(new Uint8Array(n.slice(o + 1)), i);
      const g = JSON.parse(decodeURIComponent(escape(String.fromCharCode.apply(null, c)))), d = {
        default: {
          fillColor: { r: 1, g: 120 / 255, b: 0 },
          fillOpacity: 0.8,
          strokeColor: { r: 0, g: 0, b: 0 },
          strokeOpacity: 1,
          strokeWidth: 1
        },
        rectangle: {
          fillColor: { r: 176 / 255, g: 222 / 255, b: 92 / 255 },
          strokeColor: { r: 153 / 255, g: 153 / 255, b: 153 / 255 },
          strokeWidth: 2
        },
        ellipse: {
          fillColor: { r: 176 / 255, g: 222 / 255, b: 92 / 255 },
          strokeColor: { r: 153 / 255, g: 153 / 255, b: 153 / 255 },
          strokeWidth: 2
        },
        circle: {
          fillColor: { r: 176 / 255, g: 222 / 255, b: 92 / 255 },
          strokeColor: { r: 153 / 255, g: 153 / 255, b: 153 / 255 },
          strokeWidth: 2
        },
        polyline: {
          strokeColor: { r: 1, g: 120 / 255, b: 0 },
          strokeOpacity: 0.5,
          strokeWidth: 4
        },
        polyline_closed: {
          fillColor: { r: 176 / 255, g: 222 / 255, b: 92 / 255 },
          strokeColor: { r: 153 / 255, g: 153 / 255, b: 153 / 255 },
          strokeWidth: 2
        }
      };
      if (g.props = g._elementQuery.props.map((y) => {
        const b = {};
        g._elementQuery.propskeys.forEach((L, T) => {
          b[L] = y[T];
        }), Object.assign(b, Ee(b));
        const v = b.type + (b.closed ? "_closed" : "");
        return ["fillColor", "strokeColor", "strokeWidth", "fillOpacity", "strokeOpacity"].forEach((L) => {
          b[L] === void 0 && (b[L] = (d[v] || d.default)[L]), b[L] === void 0 && (b[L] = d.default[L]);
        }), b;
      }), t = new DataView(n, i + 1, o - i - 1), t.byteLength !== g._elementQuery.returned * 28)
        throw new Error("invalid centroid data size");
      const u = {
        id: new Array(g._elementQuery.returned),
        x: new Float32Array(g._elementQuery.returned),
        y: new Float32Array(g._elementQuery.returned),
        r: new Float32Array(g._elementQuery.returned),
        s: new Uint32Array(g._elementQuery.returned)
      };
      let h, F;
      for (h = F = 0; F < t.byteLength; h += 1, F += 28)
        u.id[h] = ("0000000" + t.getUint32(F, !1).toString(16)).substr(-8) + ("0000000" + t.getUint32(F + 4, !1).toString(16)).substr(-8) + ("0000000" + t.getUint32(F + 8, !1).toString(16)).substr(-8), u.x[h] = t.getFloat32(F + 12, !0), u.y[h] = t.getFloat32(F + 16, !0), u.r[h] = t.getFloat32(F + 20, !0), u.s[h] = t.getUint32(F + 24, !0);
      return g.centroids = u, g.data = { length: g._elementQuery.returned }, g._elementQuery.count > g._elementQuery.returned && (g.partial = !0), this._centroids = g, g;
    });
  },
  /**
   * Fetch a single resource from the server. Triggers g:fetched on success,
   * or g:error on error.
   * To ignore the default error handler, pass
   *     ignoreError: true
   * in your opts object.
   */
  fetch: function(a) {
    if (this.altUrl === null && this.resourceName === null) {
      alert("Error: You must set an altUrl or a resourceName on your model.");
      return;
    }
    a = a || {};
    var e = {
      url: (this.altUrl || this.resourceName) + "/" + this.get("_id"),
      /* Add our region request into the query */
      data: Object.assign({}, this._region, { _: (this.get("updated") || this.get("created")) + "_" + this.get("_version") })
    };
    return a.extraPath && (e.url += "/" + a.extraPath), a.ignoreError && (e.error = null), this._inFetch = !0, this._refresh && (delete this._pageElements, delete this._centroids, this._refresh = !1), de(e).done((n) => {
      const i = (n.annotation || {}).elements || [];
      this.set(n), this._pageElements === void 0 && n._elementQuery && (this._pageElements = n._elementQuery.count > n._elementQuery.returned, this._pageElements ? (this._inFetch = "centroids", this.fetchCentroids().then(() => (this._inFetch = !0, a.extraPath ? this.trigger("g:fetched." + a.extraPath) : this.trigger("g:fetched"), null)).always(() => {
        if (this._inFetch = !1, this._nextFetch) {
          var o = this._nextFetch;
          this._nextFetch = null, o();
        }
        return null;
      })) : this._nextFetch = null), this._inFetch !== "centroids" && (a.extraPath ? this.trigger("g:fetched." + a.extraPath) : this.trigger("g:fetched")), this._elements.reset(i, ne.extend({ sync: !0 }, a));
    }).fail((n) => {
      this.trigger("g:error", n);
    }).always(() => {
      if (this._inFetch !== "centroids" && (this._inFetch = !1, this._nextFetch)) {
        var n = this._nextFetch;
        this._nextFetch = null, this._pageElements !== !1 && n();
      }
    });
  },
  /**
   * Get/set for a refresh flag.
   *
   * @param {boolean} [val] If specified, set the refresh flag.  If not
   *    specified, return the refresh flag.
   * @returns {boolean|this}
   */
  refresh(a) {
    return a === void 0 ? self._refresh : (self._refresh = a, this);
  },
  /**
   * Perform a PUT or POST request on the annotation data depending
   * on whether the annotation is new or not.  This mirrors somewhat
   * the api of `Backbone.Model.save`.  For new models, the `itemId`
   * attribute is required.
   */
  save(a) {
    const e = ne.extend({}, this.get("annotation"));
    let n, t;
    const i = this.isNew();
    if (i) {
      if (!this.get("itemId"))
        throw new Error("itemId is required to save new annotations");
      n = `annotation?itemId=${this.get("itemId")}`, t = "POST";
    } else
      n = `annotation/${this.id}`, t = "PUT", ee() && (this.attributes.updated = "" + Date.now(), this.attributes.updatedId = ee().id);
    return this._pageElements === !1 || i ? (this._pageElements = !1, e.elements = ne.map(e.elements, (o) => (o = ne.extend({}, o), o.label && !o.label.value && delete o.label, o))) : (delete e.elements, this._pageElements === !0 && console.warn("Cannot save elements of a paged annotation")), de({
      url: n,
      method: t,
      contentType: "application/json",
      processData: !1,
      data: JSON.stringify(e)
    }).done((o) => {
      i && (o.elements = (this.get("annotation") || {}).elements || [], this.set(o)), this.trigger("sync", this, o, a);
    });
  },
  /**
   * Perform a DELETE request on the annotation model and remove all
   * event listeners.  This mirrors the api of `Backbone.Model.destroy`
   * without the backbone specific options, which are not supported by
   * girder's base model either.
   */
  destroy(a) {
    return this.stopListening(), this.trigger("destroy", this, this.collection, a), this.delete(a);
  },
  name() {
    return (this.get("annotation") || {}).name;
  },
  /**
   * Perform a DELETE request on the annotation model and reset the id
   * attribute, but don't remove event listeners.
   */
  delete(a) {
    this.trigger("g:delete", this, this.collection, a);
    let e = !1;
    return this.isNew() || (ee() && (this.attributes.updated = "" + Date.now(), this.attributes.updatedId = ee().id), e = de({
      url: `annotation/${this.id}`,
      method: "DELETE"
    })), this.unset("_id"), e;
  },
  /**
   * Return the annotation as a geojson FeatureCollection.
   *
   * WARNING: Not all annotations are representable in geojson.
   * Annotation types that cannot be converted will be ignored.
   */
  geojson() {
    const e = (this.get("annotation") || {}).elements || [];
    return qe(e, { annotation: this.id });
  },
  /**
   * Return annotations that cannot be represented as geojson as geojs
   * features specifications.
   *
   * @param webglLayer: the parent feature layer.
   */
  non_geojson(a) {
    const n = (this.get("annotation") || {}).elements || [];
    return Ge(n, { annotation: this.id }, a);
  },
  /**
   * Return annotation elements that cannot be represented as geojs
   * features, such as image overlays.
   */
  overlays() {
    const a = ["image", "pixelmap"];
    return ((this.get("annotation") || {}).elements || []).filter((t) => a.includes(t.type));
  },
  /**
   * Set the view.  If we are paging elements, possibly refetch the elements.
   * Callers should listen for the g:fetched event to know when new elements
   * have been fetched.
   *
   * @param {object} bounds the corners of the visible region.  This is an
   *      object with left, top, right, bottom in pixels.
   * @param {number} zoom the zoom factor.
   * @param {number} maxZoom the maximum zoom factor.
   * @param {boolean} noFetch Truthy to not perform a fetch if the view
   *  changes.
   * @param {number} sizeX the maximum width to query.
   * @param {number} sizeY the maximum height to query.
   */
  setView(a, e, n, t, i, o) {
    if (!(this._pageElements === !1 || this.isNew())) {
      var c = a.right - a.left, g = a.bottom - a.top, d = c * (this._viewArea - 1) / 2, u = g * (this._viewArea - 1) / 2, h = d / 2, F = u / 2, y = this._region.left !== void 0 && a.left >= this._region.left + h && a.top >= this._region.top + F && a.right <= this._region.right - h && a.bottom <= this._region.bottom - F && Math.abs(this._lastZoom - e) < 1;
      if (!(y && !this._inFetch)) {
        if (this._pageElements || this._region.left !== void 0) {
          var b = Object.assign({}, this._region);
          if (this._region.left = Math.max(0, a.left - d), this._region.top = Math.max(0, a.top - u), this._region.right = Math.min(i || 1e6, a.right + d), this._region.bottom = Math.min(o || 1e6, a.bottom + u), this._lastZoom = e, ["left", "top", "right", "bottom", "minimumSize"].every((L) => this._region[L] === b[L]))
            return;
        }
        if (!t && !this._nextFetch) {
          var v = () => {
            this.fetch();
          };
          this._inFetch ? this._nextFetch = v : v();
        }
      }
    }
  },
  /**
   * Return a backbone collection containing the annotation elements.
   */
  elements() {
    return this._elements;
  }
});
ne.extend(le.prototype, Ut);
const Vt = girder.collections.Collection, { SORT_DESC: Dt } = girder.constants, Ze = Vt.extend({
  resourceName: "annotation",
  model: le,
  // this is a large number so that we probably never need to page
  // annotations.
  pageLimit: 1e4,
  sortField: "created",
  sortDir: Dt
});
function R(a, e, n, t) {
  if (e === !1 || e == null || !e && (a === "class" || a === "style")) return "";
  if (e === !0) return " " + (a + '="' + a + '"');
  var i = typeof e;
  return i !== "object" && i !== "function" || typeof e.toJSON != "function" || (e = e.toJSON()), typeof e == "string" || (e = JSON.stringify(e), n || e.indexOf('"') === -1) ? (n && (e = $(e)), " " + a + '="' + e + '"') : " " + a + "='" + e.replace(/'/g, "&#39;") + "'";
}
function Fe(a, e) {
  return Array.isArray(a) ? Nt(a, e) : a && typeof a == "object" ? Bt(a) : a || "";
}
function Nt(a, e) {
  for (var n, t = "", i = "", o = Array.isArray(e), c = 0; c < a.length; c++) (n = Fe(a[c])) && (o && e[c] && (n = $(n)), t = t + i + n, i = " ");
  return t;
}
function Bt(a) {
  var e = "", n = "";
  for (var t in a) t && a[t] && qt.call(a, t) && (e = e + n + t, n = " ");
  return e;
}
function $(a) {
  var e = "" + a, n = Gt.exec(e);
  if (!n) return a;
  var t, i, o, c = "";
  for (t = n.index, i = 0; t < e.length; t++) {
    switch (e.charCodeAt(t)) {
      case 34:
        o = "&quot;";
        break;
      case 38:
        o = "&amp;";
        break;
      case 60:
        o = "&lt;";
        break;
      case 62:
        o = "&gt;";
        break;
      default:
        continue;
    }
    i !== t && (c += e.substring(i, t)), i = t + 1, c += o;
  }
  return i !== t ? c + e.substring(i, t) : c;
}
var qt = Object.prototype.hasOwnProperty, Gt = /["&<>]/;
function Qe(a, e, n, t) {
  if (!(a instanceof Error)) throw a;
  if (!(typeof window > "u" && e || t)) throw a.message += " on line " + n, a;
  var i, o, c, g;
  try {
    t = t || require("fs").readFileSync(e, { encoding: "utf8" }), i = 3, o = t.split(`
`), c = Math.max(n - i, 0), g = Math.min(o.length, n + i);
  } catch (d) {
    return a.message += " - could not read from " + e + " (" + d.message + ")", void Qe(a, null, n);
  }
  i = o.slice(c, g).map(function(d, u) {
    var h = u + c + 1;
    return (h == n ? "  > " : "    ") + h + "| " + d;
  }).join(`
`), a.path = e;
  try {
    a.message = (e || "Pug") + ":" + n + `
` + i + `

` + a.message;
  } catch {
  }
  throw a;
}
function Zt(a) {
  var e = "", n, t, i;
  try {
    var o = a || {};
    (function(c, g, d, u, h, F, y, b, v, L, T) {
      if (i = 1, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<div class="g-annotation-list-header">', i = 2, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-pencil"></i>', i = 3, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + " Annotations", i = 4, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<div class="btn-group pull-right">', i = 5, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", b && (i = 6, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<a class="g-annotation-upload" title="Upload annotation">', i = 7, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-upload"></i></a>'), i = 8, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", u.length && (i = 9, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<a" + (' class="g-annotation-download"' + R("href", `${h}/annotation/item/${L.id}`, !0, !1) + ' title="Download annotations"' + R("download", `${L.get("name")}_annotations.json`, !0, !1)) + ">", i = 10, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-download"></i></a>'), i = 11, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", d >= c.ADMIN && u.length && (i = 12, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<a class="g-annotation-permissions" title="Adjust permissions">', i = 13, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-lock"></i></a>', i = 14, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<a class="g-annotation-delete" title="Delete">', i = 15, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-cancel"></i></a>'), e = e + "</div></div>", i = 17, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", u.length) {
        i = 18, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<table class="g-annotation-list table table-hover table-condensed">', i = 19, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<thead>", i = 20, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<!--", i = 21, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "th.g-annotation-select", i = 22, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + `
`, i = 22, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "  input.g-select-all(type='checkbox')-->", i = 23, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<th class="g-annotation-toggle">', i = 24, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<a" + (R("class", Fe(["g-annotation-toggle-all", F ? "disabled" : ""], [!1, !0]), !1, !1) + ' title="Hide or show all annotations"') + ">", i = 25, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug";
        let M = u.models.some((W) => v.has(W.id));
        i = 26, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", M ? (i = 27, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-eye"></i>') : (i = 29, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-eye-off"></i>'), e = e + "</a></th>", i = 30, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", (function() {
          var W = y.columns || [];
          if (typeof W.length == "number")
            for (var I = 0, D = W.length; I < D; I++) {
              var m = W[I];
              i = 31, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", (m.type !== "record" || m.value !== "controls") && (i = 32, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<th class="g-annotation-column">', i = 33, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", m.title !== void 0 ? (i = 34, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = m.title) == null ? "" : n)) : (i = 36, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = `${m.value.substr(0, 1).toUpperCase()}${m.value.substr(1)}`) == null ? "" : n)), e = e + "</th>");
            }
          else {
            var D = 0;
            for (var I in W) {
              D++;
              var m = W[I];
              i = 31, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", (m.type !== "record" || m.value !== "controls") && (i = 32, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<th class="g-annotation-column">', i = 33, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", m.title !== void 0 ? (i = 34, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = m.title) == null ? "" : n)) : (i = 36, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = `${m.value.substr(0, 1).toUpperCase()}${m.value.substr(1)}`) == null ? "" : n)), e = e + "</th>");
            }
          }
        }).call(this), i = 37, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<th class="g-annotation-actions"></th></thead>', i = 38, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<tbody>", i = 39, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", (function() {
          var W = u.models;
          if (typeof W.length == "number")
            for (var I = 0, D = W.length; I < D; I++) {
              var m = W[I];
              i = 40, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug";
              var ae = m.get("annotation").name, Z = T.get(m.get("creatorId")), z = Z ? Z.get("login") : m.get("creatorId"), Q = T.get(m.get("updatedId")), J = Q ? Q.get("login") : m.get("updatedId");
              i = 46, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<tr" + (' class="g-annotation-row"' + R("data-annotation-id", m.id, !0, !1)) + ">", i = 47, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<!--", i = 48, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "td.g-annotation-select", i = 49, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + `
`, i = 49, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "  input(type='checkbox', title='Select annotation for bulk actions')-->", i = 50, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<td class="g-annotation-toggle">', i = 51, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<a" + (R("class", Fe(["g-annotation-toggle-select", F ? "disabled" : ""], [!1, !0]), !1, !1) + ' title="Show annotation"') + ">", i = 52, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", v.has(m.id) ? (i = 53, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-eye"></i>') : (i = 55, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-eye-off"></i>'), e = e + "</a></td>", i = 56, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", (function() {
                var Y = y.columns || [];
                if (typeof Y.length == "number")
                  for (var X = 0, re = Y.length; X < re; X++) {
                    var C = Y[X];
                    if (i = 57, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", C.type !== "record" || C.value !== "controls") {
                      i = 58, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug";
                      var E;
                      C.type === "record" && C.value === "creator" ? E = z : C.type === "record" && C.value === "updatedId" ? E = J || z : C.type === "record" && C.value === "updated" ? E = E || m.get("created") : C.type === "metadata" ? (E = m.get("annotation").attributes || {}, C.value.split(".").forEach((oe) => {
                        E = (E || {})[oe];
                      })) : E = C.type === "record" ? m.get(C.value) || m.get("annotation")[C.value] : "", i = 74, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<td" + (' class="g-annotation-entry"' + R("title", E, !0, !1)) + ">", i = 75, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", C.format === "user" ? (i = 76, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<a" + R("href", `#user/${m.get(C.value) || m.get(C.value + "Id")}`, !0, !1) + ">", i = 77, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = E) == null ? "" : n) + "</a>") : C.format === "datetime" ? (i = 79, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = new g(E).toLocaleString()) == null ? "" : n)) : C.format === "date" ? (i = 81, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = new g(E).toLocaleDateString()) == null ? "" : n)) : C.format === "time" ? (i = 83, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = new g(E).toLocaleTimeString()) == null ? "" : n)) : (i = 85, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = E) == null ? "" : n)), e = e + "</td>";
                    }
                  }
                else {
                  var re = 0;
                  for (var X in Y) {
                    re++;
                    var C = Y[X];
                    if (i = 57, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", C.type !== "record" || C.value !== "controls") {
                      i = 58, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug";
                      var E;
                      C.type === "record" && C.value === "creator" ? E = z : C.type === "record" && C.value === "updatedId" ? E = J || z : C.type === "record" && C.value === "updated" ? E = E || m.get("created") : C.type === "metadata" ? (E = m.get("annotation").attributes || {}, C.value.split(".").forEach((A) => {
                        E = (E || {})[A];
                      })) : E = C.type === "record" ? m.get(C.value) || m.get("annotation")[C.value] : "", i = 74, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<td" + (' class="g-annotation-entry"' + R("title", E, !0, !1)) + ">", i = 75, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", C.format === "user" ? (i = 76, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<a" + R("href", `#user/${m.get(C.value) || m.get(C.value + "Id")}`, !0, !1) + ">", i = 77, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = E) == null ? "" : n) + "</a>") : C.format === "datetime" ? (i = 79, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = new g(E).toLocaleString()) == null ? "" : n)) : C.format === "date" ? (i = 81, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = new g(E).toLocaleDateString()) == null ? "" : n)) : C.format === "time" ? (i = 83, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = new g(E).toLocaleTimeString()) == null ? "" : n)) : (i = 85, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = E) == null ? "" : n)), e = e + "</td>";
                    }
                  }
                }
              }).call(this), i = 86, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<td class="g-annotation-actions">', i = 87, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<!--", i = 88, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "if annotation.get('_accessLevel') >= AccessType.WRITE", i = 89, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + `
`, i = 89, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "  a.g-annotation-edit(title='Edit annotation')", i = 90, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + `
`, i = 90, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "    i.icon-cog-->", i = 91, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<a" + (' class="g-annotation-download"' + R("href", `${h}/annotation/${m.id}`, !0, !1) + ' title="Download"' + R("download", `${ae}.json`, !0, !1)) + ">", i = 92, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-download"></i></a>', i = 93, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", m.get("_accessLevel") >= c.ADMIN && (i = 94, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<a class="g-annotation-permissions" title="Adjust permissions">', i = 95, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-lock"></i></a>'), i = 96, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", m.get("_accessLevel") >= c.WRITE && (i = 97, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<a class="g-annotation-delete" title="Delete">', i = 98, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-cancel"></i></a>'), e = e + "</td></tr>";
            }
          else {
            var D = 0;
            for (var I in W) {
              D++;
              var m = W[I];
              i = 40, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug";
              var ae = m.get("annotation").name, Z = T.get(m.get("creatorId")), z = Z ? Z.get("login") : m.get("creatorId"), Q = T.get(m.get("updatedId")), J = Q ? Q.get("login") : m.get("updatedId");
              i = 46, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<tr" + (' class="g-annotation-row"' + R("data-annotation-id", m.id, !0, !1)) + ">", i = 47, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<!--", i = 48, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "td.g-annotation-select", i = 49, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + `
`, i = 49, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "  input(type='checkbox', title='Select annotation for bulk actions')-->", i = 50, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<td class="g-annotation-toggle">', i = 51, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<a" + (R("class", Fe(["g-annotation-toggle-select", F ? "disabled" : ""], [!1, !0]), !1, !1) + ' title="Show annotation"') + ">", i = 52, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", v.has(m.id) ? (i = 53, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-eye"></i>') : (i = 55, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-eye-off"></i>'), e = e + "</a></td>", i = 56, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", (function() {
                var B = y.columns || [];
                if (typeof B.length == "number")
                  for (var A = 0, q = B.length; A < q; A++) {
                    var w = B[A];
                    if (i = 57, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", w.type !== "record" || w.value !== "controls") {
                      i = 58, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug";
                      var x;
                      w.type === "record" && w.value === "creator" ? x = z : w.type === "record" && w.value === "updatedId" ? x = J || z : w.type === "record" && w.value === "updated" ? x = x || m.get("created") : w.type === "metadata" ? (x = m.get("annotation").attributes || {}, w.value.split(".").forEach((fe) => {
                        x = (x || {})[fe];
                      })) : x = w.type === "record" ? m.get(w.value) || m.get("annotation")[w.value] : "", i = 74, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<td" + (' class="g-annotation-entry"' + R("title", x, !0, !1)) + ">", i = 75, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", w.format === "user" ? (i = 76, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<a" + R("href", `#user/${m.get(w.value) || m.get(w.value + "Id")}`, !0, !1) + ">", i = 77, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = x) == null ? "" : n) + "</a>") : w.format === "datetime" ? (i = 79, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = new g(x).toLocaleString()) == null ? "" : n)) : w.format === "date" ? (i = 81, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = new g(x).toLocaleDateString()) == null ? "" : n)) : w.format === "time" ? (i = 83, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = new g(x).toLocaleTimeString()) == null ? "" : n)) : (i = 85, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = x) == null ? "" : n)), e = e + "</td>";
                    }
                  }
                else {
                  var q = 0;
                  for (var A in B) {
                    q++;
                    var w = B[A];
                    if (i = 57, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", w.type !== "record" || w.value !== "controls") {
                      i = 58, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug";
                      var x;
                      w.type === "record" && w.value === "creator" ? x = z : w.type === "record" && w.value === "updatedId" ? x = J || z : w.type === "record" && w.value === "updated" ? x = x || m.get("created") : w.type === "metadata" ? (x = m.get("annotation").attributes || {}, w.value.split(".").forEach((ce) => {
                        x = (x || {})[ce];
                      })) : x = w.type === "record" ? m.get(w.value) || m.get("annotation")[w.value] : "", i = 74, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<td" + (' class="g-annotation-entry"' + R("title", x, !0, !1)) + ">", i = 75, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", w.format === "user" ? (i = 76, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<a" + R("href", `#user/${m.get(w.value) || m.get(w.value + "Id")}`, !0, !1) + ">", i = 77, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = x) == null ? "" : n) + "</a>") : w.format === "datetime" ? (i = 79, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = new g(x).toLocaleString()) == null ? "" : n)) : w.format === "date" ? (i = 81, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = new g(x).toLocaleDateString()) == null ? "" : n)) : w.format === "time" ? (i = 83, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = new g(x).toLocaleTimeString()) == null ? "" : n)) : (i = 85, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + $((n = x) == null ? "" : n)), e = e + "</td>";
                    }
                  }
                }
              }).call(this), i = 86, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<td class="g-annotation-actions">', i = 87, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<!--", i = 88, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "if annotation.get('_accessLevel') >= AccessType.WRITE", i = 89, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + `
`, i = 89, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "  a.g-annotation-edit(title='Edit annotation')", i = 90, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + `
`, i = 90, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "    i.icon-cog-->", i = 91, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + "<a" + (' class="g-annotation-download"' + R("href", `${h}/annotation/${m.id}`, !0, !1) + ' title="Download"' + R("download", `${ae}.json`, !0, !1)) + ">", i = 92, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-download"></i></a>', i = 93, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", m.get("_accessLevel") >= c.ADMIN && (i = 94, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<a class="g-annotation-permissions" title="Adjust permissions">', i = 95, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-lock"></i></a>'), i = 96, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", m.get("_accessLevel") >= c.WRITE && (i = 97, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<a class="g-annotation-delete" title="Delete">', i = 98, t = "/root/project/girder_annotation/girder_large_image_annotation/web_client/templates/annotationListWidget.pug", e = e + '<i class="icon-cancel"></i></a>'), e = e + "</td></tr>";
            }
          }
        }).call(this), e = e + "</tbody></table>";
      }
    }).call(this, "AccessType" in o ? o.AccessType : typeof AccessType < "u" ? AccessType : void 0, "Date" in o ? o.Date : typeof Date < "u" ? Date : void 0, "accessLevel" in o ? o.accessLevel : typeof accessLevel < "u" ? accessLevel : void 0, "annotations" in o ? o.annotations : typeof annotations < "u" ? annotations : void 0, "apiRoot" in o ? o.apiRoot : typeof apiRoot < "u" ? apiRoot : void 0, "canDraw" in o ? o.canDraw : typeof canDraw < "u" ? canDraw : void 0, "confList" in o ? o.confList : typeof confList < "u" ? confList : void 0, "creationAccess" in o ? o.creationAccess : typeof creationAccess < "u" ? creationAccess : void 0, "drawn" in o ? o.drawn : typeof drawn < "u" ? drawn : void 0, "item" in o ? o.item : typeof item < "u" ? item : void 0, "users" in o ? o.users : typeof users < "u" ? users : void 0);
  } catch (c) {
    Qe(c, t, i);
  }
  return e;
}
const G = girder.$, Te = girder._, { AccessType: Qt } = girder.constants, Ie = girder.utilities.EventStream, { getCurrentUser: Jt } = girder.auth, { confirm: Re } = girder.dialog, { getApiRoot: Yt, restRequest: Me } = girder.rest, Xt = girder.views.widgets.AccessWidget, Kt = girder.events, en = girder.collections.UserCollection, tn = girder.views.widgets.UploadWidget, nn = girder.views.View, an = nn.extend({
  events: {
    "click .g-annotation-toggle-select": "_displayAnnotation",
    "click .g-annotation-toggle-all": "_displayAllAnnotations",
    "click .g-annotation-delete": "_deleteAnnotation",
    "click .g-annotation-upload": "_uploadAnnotation",
    "click .g-annotation-permissions": "_changePermissions",
    "click .g-annotation-metadata": "_annotationMetadata",
    "click .g-annotation-row"(a) {
      var e = G(a.currentTarget);
      e.find(".g-annotation-toggle-select").click();
    },
    "click .g-annotation-row a,.g-annotation-toggle-select"(a) {
      a.stopPropagation();
    }
  },
  initialize() {
    this._drawn = /* @__PURE__ */ new Set(), this._viewer = null, this._sort = {
      field: "name",
      direction: 1
    }, this.collection = this.collection || new Ze([], { comparator: null }), this.users = new en(), this.listenTo(this.collection, "all", this.render), this.listenTo(this.users, "all", this.render), this.listenTo(Ie, "g:event.large_image_annotation.create", () => this.collection.fetch(null, !0)), this.listenTo(Ie, "g:event.large_image_annotation.remove", () => this.collection.fetch(null, !0)), Me({
      type: "GET",
      url: "annotation/folder/" + this.model.get("folderId") + "/create",
      error: null
    }).done((a) => {
      this.createResp = a, girder.plugins.large_image.views.ConfigView.getConfigFile(this.model.get("folderId")).done((e) => {
        this._liconfig = e || {}, this._confList = this._liconfig.annotationList || {
          columns: [{
            type: "record",
            value: "name"
          }, {
            type: "record",
            value: "creator",
            format: "user"
          }, {
            type: "record",
            value: "created",
            format: "date"
          }]
        }, this.collection.comparator = Te.constant(0), this._lastSort = this._confList.defaultSort || [{
          type: "record",
          value: "updated",
          dir: "up"
        }, {
          type: "record",
          value: "updated",
          dir: "down"
        }], this.collection.sortField = JSON.stringify(this._lastSort.reduce((n, t) => (n.push([
          (t.type === "metadata" ? "annotation.attributes." : "") + t.value,
          t.dir === "down" ? 1 : -1
        ]), t.type === "record" && n.push([
          `annotation.${t.value}`,
          t.dir === "down" ? 1 : -1
        ]), n), [])), this.collection.fetch({
          itemId: this.model.id,
          sort: this.collection.sortField || "created",
          sortdir: -1
        }).done(() => {
          this._fetchUsers();
        });
      });
    });
  },
  render() {
    return this.$el.html(Zt({
      item: this.model,
      accessLevel: this.model.getAccessLevel(),
      creationAccess: this.createResp,
      annotations: this.collection,
      users: this.users,
      canDraw: this._viewer && this._viewer.annotationAPI(),
      drawn: this._drawn,
      apiRoot: Yt(),
      confList: this._confList,
      AccessType: Qt
    })), this;
  },
  setViewer(a) {
    return this._drawn.clear(), this._viewer = a, this;
  },
  _displayAnnotation(a) {
    if (!this._viewer || !this._viewer.annotationAPI())
      return;
    const e = G(a.currentTarget).closest(".g-annotation-row"), n = e.data("annotationId"), t = this.collection.get(n), i = e.find(".g-annotation-toggle-select i.icon-eye").length;
    i ? (this._drawn.delete(n), this._viewer.removeAnnotation(t)) : (this._drawn.add(n), t.fetch().then(() => (this._drawn.has(n) && this._viewer.drawAnnotation(t), null))), e.find(".g-annotation-toggle-select i").toggleClass("icon-eye", !i).toggleClass("icon-eye-off", !!i);
    const o = this.collection.some((c) => this._drawn.has(c.id));
    this.$el.find("th.g-annotation-toggle i").toggleClass("icon-eye", !!o).toggleClass("icon-eye-off", !o);
  },
  _displayAllAnnotations(a) {
    if (!this._viewer || !this._viewer.annotationAPI())
      return;
    const e = this.collection.some((n) => this._drawn.has(n.id));
    this.collection.forEach((n) => {
      const t = n.id;
      let i = this._drawn.has(n.id);
      e && i ? (this._drawn.delete(t), this._viewer.removeAnnotation(n), i = !1) : !e && !i && (this._drawn.add(t), n.fetch().then(() => (this._drawn.has(t) && this._viewer.drawAnnotation(n), null)), i = !0), this.$el.find(`.g-annotation-row[data-annotation-id="${t}"] .g-annotation-toggle-select i`).toggleClass("icon-eye", !!i).toggleClass("icon-eye-off", !i);
    }), this.$el.find("th.g-annotation-toggle i").toggleClass("icon-eye", !e).toggleClass("icon-eye-off", !!e);
  },
  _deleteAnnotation(a) {
    const n = G(a.currentTarget).parents(".g-annotation-row").data("annotationId");
    if (!n) {
      Re({
        text: "Are you sure you want to delete <b>ALL</b> annotations?",
        escapedHtml: !0,
        yesText: "Delete",
        confirmCallback: () => {
          Me({
            url: `annotation/item/${this.model.id}`,
            method: "DELETE"
          }).done(() => {
            this.collection.fetch(null, !0);
          });
        }
      });
      return;
    }
    const t = this.collection.get(n);
    Re({
      text: `Are you sure you want to delete <b>${Te.escape(t.get("annotation").name)}</b>?`,
      escapedHtml: !0,
      yesText: "Delete",
      confirmCallback: () => {
        this._drawn.delete(n), t.destroy();
      }
    });
  },
  _uploadAnnotation() {
    var a = new tn({
      el: G("#g-dialog-container"),
      title: "Upload Annotation",
      parent: this.model,
      parentType: "item",
      parentView: this,
      multiFile: !0,
      otherParams: {
        reference: JSON.stringify({
          identifier: "LargeImageAnnotationUpload",
          itemId: this.model.id,
          fileId: this.model.get("largeImage") && this.model.get("largeImage").fileId,
          userId: (Jt() || {}).id
        })
      }
    }).on("g:uploadFinished", () => {
      Kt.trigger("g:alert", {
        icon: "ok",
        text: "Uploaded annotations.",
        type: "success",
        timeout: 4e3
      }), this.collection.fetch(null, !0);
    }, this);
    this._uploadWidget = a, a.render();
  },
  _changePermissions(a) {
    let n = G(a.currentTarget).parents(".g-annotation-row").data("annotationId");
    !n && this.collection.length === 1 && (n = this.collection.at(0).id);
    const t = n ? this.collection.get(n) : this.collection.at(0).clone();
    n || (t.get("annotation").name = "All Annotations", t.save = () => {
    }, t.updateAccess = () => {
      const i = {
        access: t.get("access"),
        public: t.get("public"),
        publicFlags: t.get("publicFlags")
      };
      this.collection.each((o) => {
        o.set(i), o.updateAccess();
      }), this.collection.fetch(null, !0), t.trigger("g:accessListSaved");
    }), new Xt({
      el: G("#g-dialog-container"),
      type: "annotation",
      hideRecurseOption: !0,
      parentView: this,
      model: t,
      noAccessFlag: !0
    }).on("g:accessListSaved", () => {
      this.collection.fetch(null, !0);
    });
  },
  _fetchUsers() {
    this.collection.each((a) => {
      this.users.add({ _id: a.get("creatorId") }), this.users.add({ _id: a.get("updatedId") });
    }), G.when.apply(G, this.users.map((a) => a.fetch())).always(() => {
      this.render();
    });
  }
}), ye = girder._, { wrap: be } = girder.utilities.PluginUtils, rn = girder.events;
rn.on("g:appload.before", function() {
  const a = girder.plugins.large_image.views.ImageViewerSelectWidget;
  be(a, "initialize", function(e, n) {
    this.itemId = n.imageModel.id, this.model = n.imageModel, this._annotationList = new an({
      model: this.model,
      parentView: this
    }), e.apply(this, ye.rest(arguments));
  }), be(a, "render", function(e) {
    return e.apply(this, ye.rest(arguments)), this.$el.append(Ft()), this._annotationList.setViewer(this.currentViewer).setElement(this.$(".g-annotation-list-container")).render(), this;
  }), be(a, "_selectViewer", function(e) {
    return e.apply(this, ye.rest(arguments)), this._annotationList.setViewer(this.currentViewer).render(), this;
  });
});
const on = girder._;
function ge(a, e) {
  return e = e || a.type(), on.extend({}, Ae[e] || {});
}
function je(a) {
  return [a.x, a.y, a.z || 0];
}
const sn = girder._;
function un(a) {
  const e = ge(a);
  return sn.extend(e, {
    type: "point",
    center: je(a.coordinates()[0])
  });
}
const ln = girder._;
function We(a) {
  const e = ge(a);
  let n = a.coordinates(), t = [
    Math.atan2(n[1].y - n[0].y, n[1].x - n[0].x),
    Math.atan2(n[2].y - n[1].y, n[2].x - n[1].x),
    Math.atan2(n[3].y - n[2].y, n[3].x - n[2].x),
    Math.atan2(n[0].y - n[3].y, n[0].x - n[3].x)
  ], i = t.indexOf(Math.min(...t));
  t[(i + 1) % 4] - t[i] > Math.PI && (n = [n[0], n[3], n[2], n[1]], t = [
    Math.atan2(n[1].y - n[0].y, n[1].x - n[0].x),
    Math.atan2(n[2].y - n[1].y, n[2].x - n[1].x),
    Math.atan2(n[3].y - n[2].y, n[3].x - n[2].x),
    Math.atan2(n[0].y - n[3].y, n[0].x - n[3].x)
  ], i = t.indexOf(Math.min(...t))), t[i] < -0.75 * Math.PI && (i += 1);
  const o = n[i % 4], c = n[(i + 1) % 4], g = n[(i + 2) % 4], d = n[(i + 3) % 4], u = [g.x - c.x, g.y - c.y], h = [c.x - o.x, c.y - o.y], F = Math.atan2(u[1], u[0]), y = Math.sqrt(h[0] * h[0] + h[1] * h[1]), b = Math.sqrt(u[0] * u[0] + u[1] * u[1]), v = [
    0.25 * (o.x + c.x + g.x + d.x),
    0.25 * (o.y + c.y + g.y + d.y),
    0
  ];
  return ln.extend(e, {
    type: "rectangle",
    center: v,
    width: b,
    height: y,
    rotation: F
  });
}
function gn(a) {
  const e = We(a);
  return e.type = "ellipse", e;
}
function cn(a) {
  const e = We(a);
  return e.type = "circle", e.radius = Math.max(e.width, e.height) / 2, delete e.width, delete e.height, delete e.rotation, delete e.normal, e;
}
const dn = girder._;
function pe(a) {
  return dn.map(a, je);
}
const hn = girder._;
function _n(a) {
  const e = ge(a, "polyline");
  let n = a.coordinates();
  const t = n.inner ? n.inner.map((i) => pe(i)) : void 0;
  return n = pe(n.outer || n), hn.extend(e, {
    type: "polyline",
    closed: !0,
    points: n,
    holes: t
  });
}
const Fn = girder._;
function pn(a) {
  const e = ge(a, "polyline"), n = pe(a.coordinates());
  return Fn.extend(e, {
    type: "polyline",
    closed: !!a.style("closed"),
    points: n
  });
}
const Ce = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  circle: cn,
  ellipse: gn,
  line: pn,
  point: un,
  polygon: _n,
  rectangle: We
}, Symbol.toStringTag, { value: "Module" })), fn = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  array: pe,
  point: je
}, Symbol.toStringTag, { value: "Module" })), mn = girder._;
function Je(a) {
  var e = a.type();
  if (!mn.has(Ce, e))
    throw new Error(
      `Unknown annotation type "${e}"`
    );
  return Ce[e](a);
}
const yn = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  common: ge,
  convert: Je,
  coordinates: fn,
  types: Ce
}, Symbol.toStringTag, { value: "Module" })), bn = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  convert: qe,
  convertFeatures: zt,
  defaults: Ae,
  geojs: yn,
  geometry: ve,
  rotate: Le,
  style: Ee
}, Symbol.toStringTag, { value: "Module" })), wn = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  AnnotationCollection: Ze,
  ElementCollection: Ne
}, Symbol.toStringTag, { value: "Module" })), vn = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  AnnotationModel: le
}, Symbol.toStringTag, { value: "Module" })), Cn = girder.$, { wrap: Ln } = girder.utilities.PluginUtils, Ye = girder.views.widgets.HierarchyWidget, { restRequest: Xe } = girder.rest, An = girder.views.widgets.AccessWidget;
Ln(Ye, "render", function(a) {
  a.call(this), this.parentModel.get("_modelType") === "folder" && En(this, this.parentModel.id);
});
function En(a, e) {
  Xe({
    type: "GET",
    url: "annotation/folder/" + e + "/present",
    data: {
      recurse: !0
    }
  }).done((n) => {
    n && xn(a);
  });
}
function xn(a) {
  a.$(".g-edit-annotation-access").length === 0 && (a.$(".g-folder-actions-menu > .divider").length > 0 ? a.$(".g-folder-actions-menu > .divider").before(
    '<li role="presentation"><a class="g-edit-annotation-access" role="menuitem"><i class="icon-lock"></i>Annotation access control</a></li>'
  ) : a.$("ul.g-folder-actions-menu").append(
    '<li role="presentation"><a class="g-edit-annotation-access" role="menuitem"><i class="icon-lock"></i>Annotation access control</a></li>'
  ), a.events["click .g-edit-annotation-access"] = jn, a.delegateEvents());
}
function jn() {
  Xe({
    type: "GET",
    url: "annotation/folder/" + this.parentModel.get("_id"),
    data: {
      recurse: !0,
      limit: 1
    }
  }).done((a) => {
    const e = new le(a[0]);
    e.get("annotation").name = "Your Annotations", e.save = () => {
    }, e.updateAccess = (n) => {
      const t = {
        access: e.get("access"),
        public: e.get("public"),
        publicFlags: e.get("publicFlags")
      }, i = new le();
      i.id = this.parentModel.get("_id"), i.altUrl = "annotation/folder", i.set(t), i.updateAccess(n), e.trigger("g:accessListSaved");
    }, e.fetchAccess(!0).done(() => {
      new An({
        // eslint-disable-line no-new
        el: Cn("#g-dialog-container"),
        modelType: "annotation",
        model: e,
        hideRecurseOption: !1,
        parentView: this,
        noAccessFlag: !0
      });
    });
  });
}
const we = girder.$, Pe = girder._, { restRequest: Wn } = girder.rest, { wrap: On } = girder.utilities.PluginUtils, Ke = girder.views.widgets.ItemListWidget;
On(Ke, "render", function(a) {
  a.apply(this, Pe.rest(arguments));
  function e(n, t, i, o) {
    const c = we('.large_image_thumbnail[g-item-cid="' + n.cid + '"]', t).first();
    if (!c.length)
      return;
    let g = c.find(".large_image_annotation_badge");
    g.length === 0 && (g = we('<div class="large_image_annotation_badge hidden"></div>').appendTo(c)), g.attr("title", o ? "Referenced by an annotation" : `${i} annotation${i === 1 ? "" : "s"}`).text(i).toggleClass("hidden", !i);
  }
  ie.getSettings((n) => {
    if (n["large_image.show_thumbnails"] === !1 || this.$(".large_image_annotation_badge").length > 0)
      return;
    const t = this.collection.toArray();
    if (!Pe.some(t, (g) => g.has("largeImage")) || this._inFetch || this._needsFetch)
      return;
    const o = t.filter((g) => g._annotationCount === void 0 && g.has("largeImage")).map((g) => (g._annotationCount = null, delete g._annotationReferenced, g.id));
    let c;
    o.length ? c = Wn({
      type: "POST",
      url: "annotation/counts",
      data: {
        items: o.join(",")
      },
      headers: { "X-HTTP-Method-Override": "GET" },
      error: null
    }).done((g) => {
      Object.entries(g).forEach(([d, u]) => {
        d === "referenced" ? Object.keys(u).forEach((h) => {
          this.collection.get(h) && (this.collection.get(h)._annotationReferenced = !0);
        }) : this.collection.get(d) && (this.collection.get(d)._annotationCount = u);
      });
    }) : c = we.Deferred().resolve({}), c.then(() => (this.collection.forEach((g) => {
      g._annotationCount !== void 0 && (g._annotationReferenced ? e(g, this.$el, "*", !0) : e(g, this.$el, g._annotationCount));
    }), null));
  });
});
const $n = girder._;
var ze = {
  /**
   * Returns whether or not the view supports drawing and rendering
   * annotations.
   */
  annotationAPI: $n.constant(!1),
  /**
   * Render an annotation model on the image.
   *
   * @param {AnnotationModel} annotation
   */
  drawAnnotation: function() {
    throw new Error("Viewer does not support drawing annotations");
  },
  /**
   * Remove an annotation from the image.  This simply
   * finds a layer with the given id and removes it because
   * each annotation is contained in its own layer.  If
   * the annotation is not drawn, this is a noop.
   *
   * @param {AnnotationModel} annotation
   */
  removeAnnotation: function() {
    throw new Error("Viewer does not support drawing annotations");
  },
  /**
   * Set the image interaction mode to region drawing mode.  This
   * method takes an optional `model` argument where the region will
   * be stored when created by the user.  In any case, this method
   * returns a promise that resolves to an array defining the region:
   *   [ left, top, width, height ]
   *
   * @param {Backbone.Model} [model] A model to set the region to
   * @returns {Promise}
   */
  drawRegion: function() {
    throw new Error("Viewer does not support drawing annotations");
  },
  /**
   * Set the image interaction mode to draw the given type of annotation.
   *
   * @param {string} type An annotation type
   * @param {object} [options]
   * @param {boolean} [options.trigger=true]
   *      Trigger a global event after creating each annotation element.
   * @returns {Promise}
   *      Resolves to an array of generated annotation elements.
   */
  startDrawMode: function() {
    throw new Error("Viewer does not support drawing annotations");
  }
};
const Sn = girder.$, O = girder._, kn = girder.Backbone, te = girder.events, { wrap: Tn } = girder.utilities.PluginUtils, { restRequest: In } = girder.rest;
function He() {
  function a() {
    return Math.floor((1 + Math.random()) * 65536).toString(16).substring(1);
  }
  return a() + a() + a() + a() + a() + a();
}
var Rn = function(a) {
  return Tn(a, "initialize", function(e) {
    var n = arguments[1];
    return this._annotations = {}, this._featureOpacity = {}, this._unclampBoundsForOverlay = !0, this._globalAnnotationOpacity = n.globalAnnotationOpacity || 1, this._globalAnnotationFillOpacity = n.globalAnnotationFillOpacity || 1, this._highlightFeatureSizeLimit = n.highlightFeatureSizeLimit || 1e4, this.listenTo(te, "s:widgetDrawRegionEvent", this.drawRegion), this.listenTo(te, "s:widgetClearRegion", this.clearRegion), this.listenTo(te, "g:startDrawMode", this.startDrawMode), this._hoverEvents = n.hoverEvents, e.apply(this, O.rest(arguments));
  }), {
    _postRender: function() {
      this.featureLayer = this.viewer.createLayer("feature", {
        features: ["point", "line", "polygon", "marker"]
      }), this.setGlobalAnnotationOpacity(this._globalAnnotationOpacity), this.setGlobalAnnotationFillOpacity(this._globalAnnotationFillOpacity), this.annotationLayer = this.viewer.createLayer("annotation", {
        annotations: ["point", "line", "rectangle", "ellipse", "circle", "polygon"],
        showLabels: !1
      });
      var e = window.geo;
      this.viewer.geoOn(e.event.pan, () => {
        this.setBounds();
      });
    },
    annotationAPI: O.constant(!0),
    /**
     * @returns whether to clamp viewer bounds when image overlays are
     * rendered
     */
    getUnclampBoundsForOverlay: function() {
      return this._unclampBoundsForOverlay;
    },
    /**
     *
     * @param {bool} newValue Set whether to clamp viewer bounds when image
     * overlays are rendered.
     */
    setUnclampBoundsForOverlay: function(e) {
      this._unclampBoundsForOverlay = e;
    },
    /**
     * Given an image overlay annotation element, compute and return
     * a proj-string representation of its transform specification.
     * @param {object} overlay A image annotation element.
     * @returns a proj-string representing how to overlay should be
     *   transformed.
     */
    _getOverlayTransformProjString: function(e) {
      const n = e.transform || {};
      let t = n.xoffset || 0, i = n.yoffset || 0;
      const o = n.matrix || [[1, 0], [0, 1]];
      let c = o[0][0], g = o[0][1], d = o[1][0], u = o[1][1];
      const h = 2 ** this._getOverlayRelativeScale(e);
      h && h !== 1 && (c /= h, g /= h, d /= h, u /= h, t *= h, i *= h);
      let F = "+proj=longlat +axis=enu";
      return t !== 0 && (t = -1 * t, F = F + ` +xoff=${t}`), i !== 0 && (F = F + ` +yoff=${i}`), (c !== 1 || g !== 0 || d !== 0 || u !== 1) && (F = F + ` +s11=${1 / c} +s12=${g} +s21=${d} +s22=${1 / u}`), F;
    },
    /**
     * Given an overlay with a transform matrix, compute an approximate
     * scale compaared to the base.
     *
     * @param {object} overlay The overlay annotation record.
     * @returns {number} The approximate scale as an integer power of two.
     */
    _getOverlayRelativeScale: function(e) {
      const t = (e.transform || {}).matrix || [[1, 0], [0, 1]], i = t[0][0], o = t[0][1], c = t[1][0], g = t[1][1], d = Math.sqrt(Math.abs(i * g - o * c)) || 1;
      return Math.floor(Math.log2(d));
    },
    /**
     * @returns The number of currently drawn overlay elements across
     * all annotations.
     */
    _countDrawnImageOverlays: function() {
      let e = 0;
      return O.each(this._annotations, (n, t, i) => {
        const o = n.overlays || [];
        e += o.length;
      }), e;
    },
    /**
     * Set additional parameters for pixelmap overlays.
     * @param {object} layerParams An object containing layer parameters. This should already have
     * generic properties for overlay annotations set, such as the URL, opacity, etc.
     * @param {object} pixelmapElement A pixelmap annotation element
     * @param {number} levelDifference The difference in zoom level between the base image and the overlay
     * @returns An object containing parameters needed to create a pixelmap layer.
     */
    _addPixelmapLayerParams(e, n, t) {
      e.keepLower = !1, O.isFunction(e.url) || t ? e.url = (g, d, u) => "api/v1/item/" + n.girderId + `/tiles/zxy/${u - t}/${g}/${d}?encoding=PNG` : e.url = e.url + "?encoding=PNG";
      let i = n.values;
      if (n.boundaries) {
        const g = new Array(i.length * 2);
        for (let d = 0; d < i.length; d++)
          g[d * 2] = g[d * 2 + 1] = i[d];
        i = g;
      }
      e.data = i;
      const o = n.categories, c = n.boundaries;
      return e.style = {
        color: (g, d) => {
          if (g < 0 || g >= o.length)
            return console.warn(`No category found at index ${g} in the category map.`), "rgba(0, 0, 0, 0)";
          let u;
          const h = o[g];
          return c ? u = d % 2 === 0 ? h.fillColor : h.strokeColor : u = h.fillColor, u;
        }
      }, e;
    },
    /**
     * Generate layer parameters for an image overlay layer
     * @param {object} overlayImageMetadata metadata such as size, tile size, and levels for the overlay image
     * @param {string} overlayImageId ID of a girder image item
     * @param {object} overlay information about the overlay such as opacity
     * @returns layer params for the image overlay layer
     */
    _generateOverlayLayerParams(e, n, t) {
      const o = window.geo.util.pixelCoordinateParams(
        this.viewer.node(),
        e.sizeX,
        e.sizeY,
        e.tileWidth,
        e.tileHeight
      );
      o.layer.useCredentials = !0, o.layer.url = `api/v1/item/${n}/tiles/zxy/{z}/{x}/{y}`, this._countDrawnImageOverlays() <= 6 ? o.layer.autoshareRenderer = !1 : o.layer.renderer = "canvas", o.layer.opacity = t.opacity || 1, o.layer.opacity *= this._globalAnnotationOpacity;
      let c = this.levels - e.levels;
      return c -= this._getOverlayRelativeScale(t), this.levels !== e.levels && (o.layer.url = (g, d, u) => "api/v1/item/" + n + `/tiles/zxy/${u - c}/${g}/${d}`, o.layer.minLevel = c, o.layer.maxLevel += c, o.layer.tilesMaxBounds = (g) => {
        var d = Math.pow(2, o.layer.maxLevel - g);
        return {
          x: Math.floor(e.sizeX / d),
          y: Math.floor(e.sizeY / d)
        };
      }, o.layer.tilesAtZoom = (g) => {
        var d = Math.pow(2, o.layer.maxLevel - g);
        return {
          x: Math.ceil(e.sizeX / e.tileWidth / d),
          y: Math.ceil(e.sizeY / e.tileHeight / d)
        };
      }), t.type === "pixelmap" ? o.layer = this._addPixelmapLayerParams(o.layer, t, c) : t.hasAlpha && (o.layer.keepLower = !1, o.layer.url = (g, d, u) => "api/v1/item/" + n + `/tiles/zxy/${u - c}/${g}/${d}?encoding=PNG`), o.layer;
    },
    /**
     * Render an annotation model on the image.  Currently, this is limited
     * to annotation types that can be (1) directly converted into geojson
     * primitives, (2) be represented as heatmaps, or (3) shown as image
     * overlays.
     *
     * Internally, this generates a new feature layer for the annotation
     * that is referenced by the annotation id.  All "elements" contained
     * inside this annotation are drawn in the referenced layer.
     *
     * @param {AnnotationModel} annotation
     * @param {object} [options]
     * @param {boolean} [options.fetch=true] Enable fetching the annotation
     *   from the server, including paging the results.  If false, it is
     *   assumed the elements already exist on the annotation object.  This
     *   is useful for temporarily showing annotations that are not
     *   propagated to the server.
     */
    drawAnnotation: function(e, n) {
      if (!this.viewer)
        return;
      var t = window.geo;
      n = O.defaults(n || {}, { fetch: !0 });
      var i = e.geojson();
      const o = e.overlays() || [];
      var c = O.has(this._annotations, e.id), g;
      let d = !1;
      if (c && (O.each(this._annotations[e.id].features, (h, F) => {
        F || !e._centroids || h.data().length !== e._centroids.data.length ? h._ownLayer ? h.layer().map().deleteLayer(h.layer()) : (this.featureLayer.deleteFeature(h), d = !0) : g = h;
      }), this._annotations[e.id].overlays && O.each(this._annotations[e.id].overlays, (h) => {
        const F = this._annotations[e.id].overlays.map((b) => b.id), y = o.map((b) => b.id);
        O.each(F, (b) => {
          if (!y.includes(b)) {
            const v = this.viewer.layers().find((L) => L.id() === b);
            this.viewer.deleteLayer(v);
          }
        });
      })), this._annotations[e.id] = {
        features: g ? [g] : [],
        options: n,
        annotation: e,
        overlays: o
      }, !(n.fetch && (!c || e.refresh() || e._inFetch === "centroids") && (e.off("g:fetched", null, this).on("g:fetched", () => {
        this.trigger(
          "g:mouseResetAnnotation",
          e
        ), this.drawAnnotation(e);
      }, this), this.setBounds({ [e.id]: this._annotations[e.id] }), e._inFetch === "centroids"))) {
        e.refresh(!1);
        var u = this._annotations[e.id].features;
        if (e._centroids && !g) {
          const h = this.featureLayer.createFeature("point");
          u.push(h), h.data(e._centroids.data).position((F, y) => ({
            x: e._centroids.centroids.x[y],
            y: e._centroids.centroids.y[y]
          })).style({
            radius: (F, y) => {
              let b = e._centroids.centroids.r[y];
              return b ? (b /= 2.5 * this.viewer.unitsPerPixel(this.viewer.zoom()), b) : 8;
            },
            stroke: (F, y) => !e._shownIds || !e._shownIds.has(e._centroids.centroids.id[y]),
            strokeColor: (F, y) => {
              const b = e._centroids.centroids.s[y];
              return e._centroids.props[b].strokeColor;
            },
            strokeOpacity: (F, y) => {
              const b = e._centroids.centroids.s[y];
              return e._centroids.props[b].strokeOpacity;
            },
            strokeWidth: (F, y) => {
              const b = e._centroids.centroids.s[y];
              return e._centroids.props[b].strokeWidth;
            },
            fill: (F, y) => !e._shownIds || !e._shownIds.has(e._centroids.centroids.id[y]),
            fillColor: (F, y) => {
              const b = e._centroids.centroids.s[y];
              return e._centroids.props[b].fillColor;
            },
            fillOpacity: (F, y) => {
              const b = e._centroids.centroids.s[y];
              return e._centroids.props[b].fillOpacity;
            }
          }), e._centroidLastZoom = void 0, h.geoOn(t.event.pan, () => {
            if (this.viewer.zoom() !== e._centroidLastZoom)
              if (e._centroidLastZoom = this.viewer.zoom(), h.verticesPerFeature) {
                const v = 2.5 * this.viewer.unitsPerPixel(this.viewer.zoom()), L = h.verticesPerFeature(), T = h.data().length, M = new Float32Array(L * T);
                for (var F = 0, y = 0; F < T; F += 1) {
                  let W = e._centroids.centroids.r[F];
                  W ? W /= v : W = 8;
                  for (var b = 0; b < L; b += 1, y += 1)
                    M[y] = W;
                }
                h.updateStyleFromArray("radius", M, !0);
              } else
                h.modified().draw();
          });
        }
        this.getUnclampBoundsForOverlay() && this._annotations[e.id].overlays.length > 0 && (this.viewer.clampBoundsY(!1), this.viewer.clampBoundsX(!1)), O.each(this._annotations[e.id].overlays, (h) => {
          const F = h.girderId;
          In({
            url: `item/${F}/tiles`
          }).done((y) => {
            if (!this.viewer)
              return;
            const b = this.viewer.layers().filter(
              (I) => I.id() === h.id
            );
            b.length > 0 && O.each(b, (I) => {
              this.viewer.deleteLayer(I);
            });
            const v = this._generateOverlayLayerParams(y, F, h), L = h.type === "pixelmap" ? "pixelmap" : "osm", T = this._getOverlayTransformProjString(h), M = this.viewer.createLayer(L, Object.assign({}, v, { id: h.id, gcs: T }));
            this.annotationLayer.moveToTop(), this.trigger("g:drawOverlayAnnotation", h, M);
            const W = t.event.feature;
            M.geoOn(
              [
                W.mousedown,
                W.mouseup,
                W.mouseclick,
                W.mouseoff,
                W.mouseon,
                W.mouseover,
                W.mouseout
              ],
              (I) => this._onMouseFeature(I, e.elements().get(h.id), M)
            ), this.viewer.scheduleAnimationFrame(this.viewer.draw, !0);
          }).fail((y) => {
            console.error(`There was an error overlaying image with ID ${F}`);
          });
        }), this._featureOpacity[e.id] = {}, t.createFileReader("geojsonReader", { layer: this.featureLayer }).read(i, (h) => {
          h.length === 0 && (h = e.non_geojson(this.featureLayer), h.length && this.featureLayer.map().draw()), O.each(h || [], (F) => {
            var y = t.event.feature;
            u.push(F), F.selectionAPI(this._hoverEvents), F.geoOn(
              [
                y.mousedown,
                y.mouseup,
                y.mouseclick,
                y.mouseoff,
                y.mouseon,
                y.mouseover,
                y.mouseout
              ],
              (v) => this._onMouseFeature(v)
            );
            const b = F.data();
            e._centroids && (e._shownIds = new Set(F.data().map((v) => v.id))), b.length <= this._highlightFeatureSizeLimit && !e._centroids && (this._featureOpacity[e.id][F.featureType] = F.data().map(({ id: v, properties: L }) => ({
              id: v,
              fillOpacity: L.fillOpacity,
              strokeOpacity: L.strokeOpacity
            })));
          }), this._mutateFeaturePropertiesForHighlight(e.id, h), e._centroids && u[0] && (u[0].verticesPerFeature ? this.viewer.scheduleAnimationFrame(() => {
            const F = u[0].verticesPerFeature(), y = u[0].data().length, b = new Float32Array(F * y);
            for (let v = 0, L = 0; v < y; v += 1) {
              const T = e._shownIds.has(e._centroids.centroids.id[v]) ? 0 : 1;
              for (let M = 0; M < F; M += 1, L += 1)
                b[L] = T;
            }
            u[0].updateStyleFromArray({
              stroke: b,
              fill: b
            }, void 0, !0);
          }) : u[0].modified()), this.viewer.scheduleAnimationFrame(this.viewer.draw, !0);
        }), d && this.featureLayer._update();
      }
    },
    /**
     * Highlight the given annotation/element by reducing the opacity of all
     * other elements by 75%.  For performance reasons, features with a large
     * number of elements are not modified.  The limit for this behavior is
     * configurable via the constructor option `highlightFeatureSizeLimit`.
     *
     * Both arguments are optional.  If no element is provided, then all
     * elements in the given annotation are highlighted.  If no annotation
     * is provided, then highlighting state is reset and the original
     * opacities are used for all elements.
     *
     * @param {string?} annotation The id of the annotation to highlight
     * @param {string?} element The id of the element to highlight
     */
    highlightAnnotation: function(e, n) {
      return (e !== this._highlightAnnotation || n !== this._highlightElement) && (this._highlightAnnotation = e, this._highlightElement = n, O.each(this._annotations, (t, i) => {
        const o = t.features;
        this._mutateFeaturePropertiesForHighlight(i, o);
      }), this.viewer.scheduleAnimationFrame(this.viewer.draw)), this;
    },
    /**
     * Hide the given annotation/element by settings its opacity to 0.  See
     * highlightAnnotation for caveats.
     *
     * If either argument is not provided, hiding is turned off.
     *
     * @param {string?} annotation The id of the annotation to hide
     * @param {string?} element The id of the element to hide
     */
    hideAnnotation: function(e, n) {
      return this._hideAnnotation = e, this._hideElement = n, O.each(this._annotations, (t, i) => {
        const o = t.features;
        this._mutateFeaturePropertiesForHighlight(i, o);
      }), this.viewer.scheduleAnimationFrame(this.viewer.draw), this;
    },
    /**
     * Use geojs's `updateStyleFromArray` to modify the opacities of alli
     * elements in a feature.  This method uses the private attributes
     * `_highlightAnntotation` and `_highlightElement` to determine which
     * element to modify.
     */
    _mutateFeaturePropertiesForHighlight: function(e, n) {
      O.each(n, (i) => {
        const o = this._featureOpacity[e][i.featureType];
        if (!o)
          return;
        var c = {
          datalen: o.length,
          annotationId: e,
          fillOpacity: this._globalAnnotationFillOpacity,
          highlightannot: this._highlightAnnotation,
          highlightelem: this._highlightElement,
          hideannot: this._hideAnnotation,
          hideelem: this._hideElement
        };
        if (O.isMatch(i._lastFeatureProp, c))
          return;
        const g = new Array(o.length), d = new Array(o.length);
        for (let u = 0; u < o.length; u += 1) {
          const h = o[u].id, F = o[u].fillOpacity * this._globalAnnotationFillOpacity, y = o[u].strokeOpacity;
          this._hideAnnotation && e === this._hideAnnotation && h === this._hideElement ? (g[u] = 0, d[u] = 0) : !this._highlightAnnotation || !this._highlightElement && e === this._highlightAnnotation || this._highlightElement === h ? (g[u] = F, d[u] = y) : (g[u] = F * 0.25, d[u] = y * 0.25);
        }
        i.updateStyleFromArray("fillOpacity", g), i.updateStyleFromArray("strokeOpacity", d), i._lastFeatureProp = c;
      });
      const t = this._annotations[e].overlays || null;
      t && O.each(t, (i) => {
        const o = this.viewer.layers().find((c) => c.id() === i.id);
        if (o) {
          let c = (i.opacity || 1) * this._globalAnnotationOpacity;
          this._highlightAnnotation && e !== this._highlightAnnotation && (c = c * 0.25), o.opacity(c);
        }
      });
    },
    /**
     * When the image visible bounds change, or an annotation is first created,
     * set the view information for any annotation which requires it.
     *
     * @param {object} [annotations] If set, a dictionary where the keys are
     *      annotation ids and the values are an object which includes the
     *      annotation options and a reference to the annotation.  If not
     *      specified, use `this._annotations` and update the view for all
     *      relevant annotatioins.
     */
    setBounds: function(e) {
      var n = this.viewer.zoom(), t = this.viewer.bounds(), i = this.viewer.zoomRange();
      O.each(e || this._annotations, (o) => {
        o.options.fetch && o.annotation.setView && o.annotation.setView(t, n, i.max, void 0, this.sizeX, this.sizeY);
      });
    },
    /**
     * Remove an annotation from the image.  If the annotation is not
     * drawn, this does nothing.
     *
     * @param {AnnotationModel} annotation
     */
    removeAnnotation: function(e) {
      e.off("g:fetched", null, this), this.trigger(
        "g:mouseResetAnnotation",
        e
      ), O.has(this._annotations, e.id) && (O.each(this._annotations[e.id].features, (n) => {
        n._ownLayer ? n.layer().map().deleteLayer(n.layer()) : this.featureLayer.deleteFeature(n);
      }), O.each(this._annotations[e.id].overlays, (n) => {
        const t = this.viewer.layers().filter(
          (i) => i.id() === n.id
        );
        O.each(t, (i) => {
          this.trigger("g:removeOverlayAnnotation", n, i), this.viewer.deleteLayer(i);
        });
      }), delete this._annotations[e.id], delete this._featureOpacity[e.id], this._countDrawnImageOverlays() === 0 && this.getUnclampBoundsForOverlay() && (this.viewer.clampBoundsY(!0), this.viewer.clampBoundsX(!0)), this.viewer.scheduleAnimationFrame(this.viewer.draw));
    },
    /**
     * Combine two regions into a multipolygon region.
     */
    _mergeRegions(e, n) {
      return !e || !e.length || e.length < 2 || e === [-1, -1, -1, -1] ? n : (e.length === 4 ? e = [
        e[0],
        e[1],
        e[0] + e[2],
        e[1],
        e[0] + e[2],
        e[1] + e[3],
        e[0],
        e[1] + e[3]
      ] : e.length === 6 && (e = [
        e[0] - e[3],
        e[1] - e[4],
        e[0] + e[3],
        e[1] - e[4],
        e[0] + e[3],
        e[1] + e[4],
        e[0] - e[3],
        e[1] + e[4]
      ]), n.length === 4 ? n = [
        n[0],
        n[1],
        n[0] + n[2],
        n[1],
        n[0] + n[2],
        n[1] + n[3],
        n[0],
        n[1] + n[3]
      ] : n.length === 6 && (n = [
        n[0] - n[3],
        n[1] - n[4],
        n[0] + n[3],
        n[1] - n[4],
        n[0] + n[3],
        n[1] + n[4],
        n[0] - n[3],
        n[1] + n[4]
      ]), e.length === 2 && n.length === 2 && (n = [n[0], n[1], -1, -1]), e.concat([-1, -1]).concat(n));
    },
    /**
     * Set the image interaction mode to region drawing mode.  This
     * method takes an optional `model` argument where the region will
     * be stored when created by the user.  In any case, this method
     * returns a promise that resolves to an array defining the region:
     *   [ left, top, width, height ]
     *
     * @param {Backbone.Model|Object} [model] A model to set the region to,
     *   or an object with model, mode, add, and submitCtrl.
     * @param {string} [drawMode='rectangle'] An annotation drawing mode.
     * @param {boolean} [addToExisting=false] If truthy, add the new
     *   annotation to any existing annotation making a multipolygon.
     * @returns {$.Promise}
     */
    drawRegion: function(e, n, t) {
      let i, o;
      e && e.model && e.add !== void 0 && (n = e.mode, t = e.add, i = e.submitCtrl, o = e.event, e = e.model), e = e || new kn.Model();
      const c = ["polygon", "line", "point", "rectangle"].includes(n) ? n : n === "polyline" ? "line" : o ? n : "rectangle";
      return this.startDrawMode(c, { trigger: !1, signalModeChange: !0 }).then((g) => {
        var d = g[0];
        let u = "-1,-1,-1,-1";
        switch (n) {
          case "point":
            u = [Math.round(d.center[0]), Math.round(d.center[1])];
            break;
          case "line":
            u = d.points.map(([v, L, T]) => [Math.round(v), Math.round(L)]).flat(), u = u.slice(0, 4), u.push(-2), u.push(-2), u.push(-2), u.push(-2);
            break;
          case "polyline":
            for (u = d.points.map(([v, L, T]) => [Math.round(v), Math.round(L)]).flat(), u.push(-2), u.push(-2); u.length > 0 && u.length <= 6; )
              u.push(-2), u.push(-2);
            break;
          case "polygon":
            for (u = d.points.map(([v, L, T]) => [Math.round(v), Math.round(L)]).flat(); u.length > 0 && u.length <= 6; )
              u.push(u[0]), u.push(u[1]);
            break;
          default:
            var h = Math.round(d.center[0] - d.width / 2), F = Math.round(d.center[1] - d.height / 2), y = Math.round(d.width), b = Math.round(d.height);
            u = [h, F, y, b];
            break;
        }
        return t && (u = this._mergeRegions(e.get("value"), u)), e.set("value", u, { trigger: !0 }), te.trigger("li:drawRegionUpdate", { values: u, submit: i, originalEvent: o }), e.get("value");
      });
    },
    clearRegion: function(e) {
      e && e.set("value", [-1, -1, -1, -1], { trigger: !0 });
    },
    /**
     * Set the image interaction mode to draw the given type of annotation.
     *
     * @param {string} type An annotation type, or null to turn off
     *    drawing.
     * @param {object} [options]
     * @param {boolean} [options.trigger=true] Trigger a global event after
     *    creating each annotation element.
     * @param {boolean} [options.keepExisting=false] If true, don't
     *    remove extant annotations.
     * @param {object} [options.modeOptions] Additional options to pass to
     *    the annotationLayer mode.
     * @returns {$.Promise}
     *    Resolves to an array of generated annotation elements.
     */
    startDrawMode: function(e, n) {
      var t = this.annotationLayer, i = [], o = [], c = Sn.Deferred(), g;
      return t.geoOff(window.geo.event.annotation.mode), t.mode(null), t.geoOff(window.geo.event.annotation.state), n = O.defaults(n || {}, { trigger: !0 }), n.keepExisting || t.removeAllAnnotations(), t.geoOn(
        window.geo.event.annotation.state,
        (d) => {
          if (d.annotation.state() !== window.geo.annotation.state.done)
            return;
          t.geoOff(window.geo.event.annotation.mode);
          const u = {};
          t.currentBooleanOperation && (u.currentBooleanOperation = t.currentBooleanOperation()), g = Je(d.annotation), g.id || (g.id = He()), i.push(g), o.push(d.annotation), n.trigger && te.trigger("g:annotationCreated", g, d.annotation, u), t.removeAllAnnotations(), t.geoOff(window.geo.event.annotation.state), c.resolve(i, o, u);
        }
      ), t.mode(e, void 0, n.modeOptions), t.geoOn(window.geo.event.annotation.mode, (d) => {
        t.geoOff(window.geo.event.annotation.state), t.geoOff(window.geo.event.annotation.mode), n.signalModeChange && te.trigger("li:drawModeChange", { event: d }), c.reject();
      }), c.promise();
    },
    setGlobalAnnotationOpacity: function(e) {
      return this._globalAnnotationOpacity = e, this.featureLayer && this.featureLayer.opacity(e), Object.values(this._annotations).forEach((n) => n.features.forEach((t) => {
        t._ownLayer && t.layer().opacity(e);
      })), O.each(this._annotations, (n) => {
        O.each(n.overlays, (t) => {
          const i = this.viewer.layers().find((o) => o.id() === t.id);
          if (i) {
            const o = t.opacity || 1;
            i.opacity(e * o);
          }
        });
      }), this;
    },
    setGlobalAnnotationFillOpacity: function(e) {
      return this._globalAnnotationFillOpacity = e, this.featureLayer && (O.each(this._annotations, (n, t) => {
        const i = n.features;
        this._mutateFeaturePropertiesForHighlight(t, i);
      }), this.viewer.scheduleAnimationFrame(this.viewer.draw)), this;
    },
    _setEventTypes: function() {
      var e = window.geo.event.feature;
      this._eventTypes = {
        [e.mousedown]: "g:mouseDownAnnotation",
        [e.mouseup]: "g:mouseUpAnnotation",
        [e.mouseclick]: "g:mouseClickAnnotation",
        [e.mouseoff]: "g:mouseOffAnnotation",
        [e.mouseon]: "g:mouseOnAnnotation",
        [e.mouseover]: "g:mouseOverAnnotation",
        [e.mouseout]: "g:mouseOutAnnotation"
      };
    },
    _onMouseFeature: function(e, n, t) {
      var i = e.data.properties || {}, o;
      if (this._eventTypes || this._setEventTypes(), i.element && i.annotation)
        o = this._eventTypes[e.event], o && this.trigger(
          o,
          i.element,
          i.annotation,
          e
        );
      else if (n && t && (o = this._eventTypes[e.event], o)) {
        const c = o + "Overlay";
        this.trigger(c, n, t, e);
      }
    },
    _guid: He
  };
};
const Ue = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  geojs: Rn
}, Symbol.toStringTag, { value: "Module" })), et = {};
for (var he in girder.plugins.large_image.views.imageViewerWidget) {
  const a = girder.plugins.large_image.views.imageViewerWidget[he];
  if (Object.keys(ze).forEach(function(e) {
    a.prototype[e] = ze[e];
  }), Ue[he]) {
    const e = Ue[he](a);
    Object.keys(e).forEach(function(n) {
      a.prototype[n] = e[n];
    });
  }
  et[he] = a;
}
const Mn = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  ConfigView: ie,
  HierarchyWidget: Ye,
  ItemListWidget: Ke,
  ViewerWidget: et
}, Symbol.toStringTag, { value: "Module" })), Pn = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  annotations: bn,
  collections: wn,
  models: vn,
  views: Mn
}, Symbol.toStringTag, { value: "Module" })), zn = girder.views.widgets.SearchFieldWidget, { registerPluginNamespace: Hn } = girder.pluginUtils;
Hn("large_image_annotation", Pn);
zn.addMode(
  "li_annotation_metadata",
  ["item"],
  "Annotation Metadata search",
  'You can search specific annotation metadata keys by adding "key:<key name>" to your search.  Otherwise, all primary metadata keys are searched.  For example "key:quality good" would find any items with annotations that have attributes with a key named quality (case sensitive) that contains the word "good" (case insensitive) anywhere in its value.'
);
//# sourceMappingURL=girder-plugin-large-image-annotation.js.map
