/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const t$2 = globalThis, e$2 = t$2.ShadowRoot && (void 0 === t$2.ShadyCSS || t$2.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, s$2 = Symbol(), o$4 = /* @__PURE__ */ new WeakMap();
let n$3 = class n {
  constructor(t2, e2, o2) {
    if (this._$cssResult$ = true, o2 !== s$2) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = t2, this.t = e2;
  }
  get styleSheet() {
    let t2 = this.o;
    const s2 = this.t;
    if (e$2 && void 0 === t2) {
      const e2 = void 0 !== s2 && 1 === s2.length;
      e2 && (t2 = o$4.get(s2)), void 0 === t2 && ((this.o = t2 = new CSSStyleSheet()).replaceSync(this.cssText), e2 && o$4.set(s2, t2));
    }
    return t2;
  }
  toString() {
    return this.cssText;
  }
};
const r$4 = (t2) => new n$3("string" == typeof t2 ? t2 : t2 + "", void 0, s$2), i$3 = (t2, ...e2) => {
  const o2 = 1 === t2.length ? t2[0] : e2.reduce((e3, s2, o3) => e3 + ((t3) => {
    if (true === t3._$cssResult$) return t3.cssText;
    if ("number" == typeof t3) return t3;
    throw Error("Value passed to 'css' function must be a 'css' function result: " + t3 + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
  })(s2) + t2[o3 + 1], t2[0]);
  return new n$3(o2, t2, s$2);
}, S$1 = (s2, o2) => {
  if (e$2) s2.adoptedStyleSheets = o2.map((t2) => t2 instanceof CSSStyleSheet ? t2 : t2.styleSheet);
  else for (const e2 of o2) {
    const o3 = document.createElement("style"), n3 = t$2.litNonce;
    void 0 !== n3 && o3.setAttribute("nonce", n3), o3.textContent = e2.cssText, s2.appendChild(o3);
  }
}, c$2 = e$2 ? (t2) => t2 : (t2) => t2 instanceof CSSStyleSheet ? ((t3) => {
  let e2 = "";
  for (const s2 of t3.cssRules) e2 += s2.cssText;
  return r$4(e2);
})(t2) : t2;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const { is: i$2, defineProperty: e$1, getOwnPropertyDescriptor: h$1, getOwnPropertyNames: r$3, getOwnPropertySymbols: o$3, getPrototypeOf: n$2 } = Object, a$1 = globalThis, c$1 = a$1.trustedTypes, l$1 = c$1 ? c$1.emptyScript : "", p$1 = a$1.reactiveElementPolyfillSupport, d$1 = (t2, s2) => t2, u$1 = { toAttribute(t2, s2) {
  switch (s2) {
    case Boolean:
      t2 = t2 ? l$1 : null;
      break;
    case Object:
    case Array:
      t2 = null == t2 ? t2 : JSON.stringify(t2);
  }
  return t2;
}, fromAttribute(t2, s2) {
  let i2 = t2;
  switch (s2) {
    case Boolean:
      i2 = null !== t2;
      break;
    case Number:
      i2 = null === t2 ? null : Number(t2);
      break;
    case Object:
    case Array:
      try {
        i2 = JSON.parse(t2);
      } catch (t3) {
        i2 = null;
      }
  }
  return i2;
} }, f$1 = (t2, s2) => !i$2(t2, s2), b$1 = { attribute: true, type: String, converter: u$1, reflect: false, useDefault: false, hasChanged: f$1 };
Symbol.metadata ?? (Symbol.metadata = Symbol("metadata")), a$1.litPropertyMetadata ?? (a$1.litPropertyMetadata = /* @__PURE__ */ new WeakMap());
let y$1 = class y extends HTMLElement {
  static addInitializer(t2) {
    this._$Ei(), (this.l ?? (this.l = [])).push(t2);
  }
  static get observedAttributes() {
    return this.finalize(), this._$Eh && [...this._$Eh.keys()];
  }
  static createProperty(t2, s2 = b$1) {
    if (s2.state && (s2.attribute = false), this._$Ei(), this.prototype.hasOwnProperty(t2) && ((s2 = Object.create(s2)).wrapped = true), this.elementProperties.set(t2, s2), !s2.noAccessor) {
      const i2 = Symbol(), h2 = this.getPropertyDescriptor(t2, i2, s2);
      void 0 !== h2 && e$1(this.prototype, t2, h2);
    }
  }
  static getPropertyDescriptor(t2, s2, i2) {
    const { get: e2, set: r2 } = h$1(this.prototype, t2) ?? { get() {
      return this[s2];
    }, set(t3) {
      this[s2] = t3;
    } };
    return { get: e2, set(s3) {
      const h2 = e2?.call(this);
      r2?.call(this, s3), this.requestUpdate(t2, h2, i2);
    }, configurable: true, enumerable: true };
  }
  static getPropertyOptions(t2) {
    return this.elementProperties.get(t2) ?? b$1;
  }
  static _$Ei() {
    if (this.hasOwnProperty(d$1("elementProperties"))) return;
    const t2 = n$2(this);
    t2.finalize(), void 0 !== t2.l && (this.l = [...t2.l]), this.elementProperties = new Map(t2.elementProperties);
  }
  static finalize() {
    if (this.hasOwnProperty(d$1("finalized"))) return;
    if (this.finalized = true, this._$Ei(), this.hasOwnProperty(d$1("properties"))) {
      const t3 = this.properties, s2 = [...r$3(t3), ...o$3(t3)];
      for (const i2 of s2) this.createProperty(i2, t3[i2]);
    }
    const t2 = this[Symbol.metadata];
    if (null !== t2) {
      const s2 = litPropertyMetadata.get(t2);
      if (void 0 !== s2) for (const [t3, i2] of s2) this.elementProperties.set(t3, i2);
    }
    this._$Eh = /* @__PURE__ */ new Map();
    for (const [t3, s2] of this.elementProperties) {
      const i2 = this._$Eu(t3, s2);
      void 0 !== i2 && this._$Eh.set(i2, t3);
    }
    this.elementStyles = this.finalizeStyles(this.styles);
  }
  static finalizeStyles(s2) {
    const i2 = [];
    if (Array.isArray(s2)) {
      const e2 = new Set(s2.flat(1 / 0).reverse());
      for (const s3 of e2) i2.unshift(c$2(s3));
    } else void 0 !== s2 && i2.push(c$2(s2));
    return i2;
  }
  static _$Eu(t2, s2) {
    const i2 = s2.attribute;
    return false === i2 ? void 0 : "string" == typeof i2 ? i2 : "string" == typeof t2 ? t2.toLowerCase() : void 0;
  }
  constructor() {
    super(), this._$Ep = void 0, this.isUpdatePending = false, this.hasUpdated = false, this._$Em = null, this._$Ev();
  }
  _$Ev() {
    this._$ES = new Promise((t2) => this.enableUpdating = t2), this._$AL = /* @__PURE__ */ new Map(), this._$E_(), this.requestUpdate(), this.constructor.l?.forEach((t2) => t2(this));
  }
  addController(t2) {
    (this._$EO ?? (this._$EO = /* @__PURE__ */ new Set())).add(t2), void 0 !== this.renderRoot && this.isConnected && t2.hostConnected?.();
  }
  removeController(t2) {
    this._$EO?.delete(t2);
  }
  _$E_() {
    const t2 = /* @__PURE__ */ new Map(), s2 = this.constructor.elementProperties;
    for (const i2 of s2.keys()) this.hasOwnProperty(i2) && (t2.set(i2, this[i2]), delete this[i2]);
    t2.size > 0 && (this._$Ep = t2);
  }
  createRenderRoot() {
    const t2 = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
    return S$1(t2, this.constructor.elementStyles), t2;
  }
  connectedCallback() {
    this.renderRoot ?? (this.renderRoot = this.createRenderRoot()), this.enableUpdating(true), this._$EO?.forEach((t2) => t2.hostConnected?.());
  }
  enableUpdating(t2) {
  }
  disconnectedCallback() {
    this._$EO?.forEach((t2) => t2.hostDisconnected?.());
  }
  attributeChangedCallback(t2, s2, i2) {
    this._$AK(t2, i2);
  }
  _$ET(t2, s2) {
    const i2 = this.constructor.elementProperties.get(t2), e2 = this.constructor._$Eu(t2, i2);
    if (void 0 !== e2 && true === i2.reflect) {
      const h2 = (void 0 !== i2.converter?.toAttribute ? i2.converter : u$1).toAttribute(s2, i2.type);
      this._$Em = t2, null == h2 ? this.removeAttribute(e2) : this.setAttribute(e2, h2), this._$Em = null;
    }
  }
  _$AK(t2, s2) {
    const i2 = this.constructor, e2 = i2._$Eh.get(t2);
    if (void 0 !== e2 && this._$Em !== e2) {
      const t3 = i2.getPropertyOptions(e2), h2 = "function" == typeof t3.converter ? { fromAttribute: t3.converter } : void 0 !== t3.converter?.fromAttribute ? t3.converter : u$1;
      this._$Em = e2;
      const r2 = h2.fromAttribute(s2, t3.type);
      this[e2] = r2 ?? this._$Ej?.get(e2) ?? r2, this._$Em = null;
    }
  }
  requestUpdate(t2, s2, i2, e2 = false, h2) {
    if (void 0 !== t2) {
      const r2 = this.constructor;
      if (false === e2 && (h2 = this[t2]), i2 ?? (i2 = r2.getPropertyOptions(t2)), !((i2.hasChanged ?? f$1)(h2, s2) || i2.useDefault && i2.reflect && h2 === this._$Ej?.get(t2) && !this.hasAttribute(r2._$Eu(t2, i2)))) return;
      this.C(t2, s2, i2);
    }
    false === this.isUpdatePending && (this._$ES = this._$EP());
  }
  C(t2, s2, { useDefault: i2, reflect: e2, wrapped: h2 }, r2) {
    i2 && !(this._$Ej ?? (this._$Ej = /* @__PURE__ */ new Map())).has(t2) && (this._$Ej.set(t2, r2 ?? s2 ?? this[t2]), true !== h2 || void 0 !== r2) || (this._$AL.has(t2) || (this.hasUpdated || i2 || (s2 = void 0), this._$AL.set(t2, s2)), true === e2 && this._$Em !== t2 && (this._$Eq ?? (this._$Eq = /* @__PURE__ */ new Set())).add(t2));
  }
  async _$EP() {
    this.isUpdatePending = true;
    try {
      await this._$ES;
    } catch (t3) {
      Promise.reject(t3);
    }
    const t2 = this.scheduleUpdate();
    return null != t2 && await t2, !this.isUpdatePending;
  }
  scheduleUpdate() {
    return this.performUpdate();
  }
  performUpdate() {
    if (!this.isUpdatePending) return;
    if (!this.hasUpdated) {
      if (this.renderRoot ?? (this.renderRoot = this.createRenderRoot()), this._$Ep) {
        for (const [t4, s3] of this._$Ep) this[t4] = s3;
        this._$Ep = void 0;
      }
      const t3 = this.constructor.elementProperties;
      if (t3.size > 0) for (const [s3, i2] of t3) {
        const { wrapped: t4 } = i2, e2 = this[s3];
        true !== t4 || this._$AL.has(s3) || void 0 === e2 || this.C(s3, void 0, i2, e2);
      }
    }
    let t2 = false;
    const s2 = this._$AL;
    try {
      t2 = this.shouldUpdate(s2), t2 ? (this.willUpdate(s2), this._$EO?.forEach((t3) => t3.hostUpdate?.()), this.update(s2)) : this._$EM();
    } catch (s3) {
      throw t2 = false, this._$EM(), s3;
    }
    t2 && this._$AE(s2);
  }
  willUpdate(t2) {
  }
  _$AE(t2) {
    this._$EO?.forEach((t3) => t3.hostUpdated?.()), this.hasUpdated || (this.hasUpdated = true, this.firstUpdated(t2)), this.updated(t2);
  }
  _$EM() {
    this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = false;
  }
  get updateComplete() {
    return this.getUpdateComplete();
  }
  getUpdateComplete() {
    return this._$ES;
  }
  shouldUpdate(t2) {
    return true;
  }
  update(t2) {
    this._$Eq && (this._$Eq = this._$Eq.forEach((t3) => this._$ET(t3, this[t3]))), this._$EM();
  }
  updated(t2) {
  }
  firstUpdated(t2) {
  }
};
y$1.elementStyles = [], y$1.shadowRootOptions = { mode: "open" }, y$1[d$1("elementProperties")] = /* @__PURE__ */ new Map(), y$1[d$1("finalized")] = /* @__PURE__ */ new Map(), p$1?.({ ReactiveElement: y$1 }), (a$1.reactiveElementVersions ?? (a$1.reactiveElementVersions = [])).push("2.1.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const t$1 = globalThis, i$1 = (t2) => t2, s$1 = t$1.trustedTypes, e = s$1 ? s$1.createPolicy("lit-html", { createHTML: (t2) => t2 }) : void 0, h = "$lit$", o$2 = `lit$${Math.random().toFixed(9).slice(2)}$`, n$1 = "?" + o$2, r$2 = `<${n$1}>`, l = document, c = () => l.createComment(""), a = (t2) => null === t2 || "object" != typeof t2 && "function" != typeof t2, u = Array.isArray, d = (t2) => u(t2) || "function" == typeof t2?.[Symbol.iterator], f = "[ 	\n\f\r]", v = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, _ = /-->/g, m = />/g, p = RegExp(`>|${f}(?:([^\\s"'>=/]+)(${f}*=${f}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`, "g"), g = /'/g, $ = /"/g, y2 = /^(?:script|style|textarea|title)$/i, x = (t2) => (i2, ...s2) => ({ _$litType$: t2, strings: i2, values: s2 }), b = x(1), E = Symbol.for("lit-noChange"), A = Symbol.for("lit-nothing"), C = /* @__PURE__ */ new WeakMap(), P = l.createTreeWalker(l, 129);
function V(t2, i2) {
  if (!u(t2) || !t2.hasOwnProperty("raw")) throw Error("invalid template strings array");
  return void 0 !== e ? e.createHTML(i2) : i2;
}
const N = (t2, i2) => {
  const s2 = t2.length - 1, e2 = [];
  let n3, l2 = 2 === i2 ? "<svg>" : 3 === i2 ? "<math>" : "", c2 = v;
  for (let i3 = 0; i3 < s2; i3++) {
    const s3 = t2[i3];
    let a2, u2, d2 = -1, f2 = 0;
    for (; f2 < s3.length && (c2.lastIndex = f2, u2 = c2.exec(s3), null !== u2); ) f2 = c2.lastIndex, c2 === v ? "!--" === u2[1] ? c2 = _ : void 0 !== u2[1] ? c2 = m : void 0 !== u2[2] ? (y2.test(u2[2]) && (n3 = RegExp("</" + u2[2], "g")), c2 = p) : void 0 !== u2[3] && (c2 = p) : c2 === p ? ">" === u2[0] ? (c2 = n3 ?? v, d2 = -1) : void 0 === u2[1] ? d2 = -2 : (d2 = c2.lastIndex - u2[2].length, a2 = u2[1], c2 = void 0 === u2[3] ? p : '"' === u2[3] ? $ : g) : c2 === $ || c2 === g ? c2 = p : c2 === _ || c2 === m ? c2 = v : (c2 = p, n3 = void 0);
    const x2 = c2 === p && t2[i3 + 1].startsWith("/>") ? " " : "";
    l2 += c2 === v ? s3 + r$2 : d2 >= 0 ? (e2.push(a2), s3.slice(0, d2) + h + s3.slice(d2) + o$2 + x2) : s3 + o$2 + (-2 === d2 ? i3 : x2);
  }
  return [V(t2, l2 + (t2[s2] || "<?>") + (2 === i2 ? "</svg>" : 3 === i2 ? "</math>" : "")), e2];
};
class S {
  constructor({ strings: t2, _$litType$: i2 }, e2) {
    let r2;
    this.parts = [];
    let l2 = 0, a2 = 0;
    const u2 = t2.length - 1, d2 = this.parts, [f2, v2] = N(t2, i2);
    if (this.el = S.createElement(f2, e2), P.currentNode = this.el.content, 2 === i2 || 3 === i2) {
      const t3 = this.el.content.firstChild;
      t3.replaceWith(...t3.childNodes);
    }
    for (; null !== (r2 = P.nextNode()) && d2.length < u2; ) {
      if (1 === r2.nodeType) {
        if (r2.hasAttributes()) for (const t3 of r2.getAttributeNames()) if (t3.endsWith(h)) {
          const i3 = v2[a2++], s2 = r2.getAttribute(t3).split(o$2), e3 = /([.?@])?(.*)/.exec(i3);
          d2.push({ type: 1, index: l2, name: e3[2], strings: s2, ctor: "." === e3[1] ? I : "?" === e3[1] ? L : "@" === e3[1] ? z : H }), r2.removeAttribute(t3);
        } else t3.startsWith(o$2) && (d2.push({ type: 6, index: l2 }), r2.removeAttribute(t3));
        if (y2.test(r2.tagName)) {
          const t3 = r2.textContent.split(o$2), i3 = t3.length - 1;
          if (i3 > 0) {
            r2.textContent = s$1 ? s$1.emptyScript : "";
            for (let s2 = 0; s2 < i3; s2++) r2.append(t3[s2], c()), P.nextNode(), d2.push({ type: 2, index: ++l2 });
            r2.append(t3[i3], c());
          }
        }
      } else if (8 === r2.nodeType) if (r2.data === n$1) d2.push({ type: 2, index: l2 });
      else {
        let t3 = -1;
        for (; -1 !== (t3 = r2.data.indexOf(o$2, t3 + 1)); ) d2.push({ type: 7, index: l2 }), t3 += o$2.length - 1;
      }
      l2++;
    }
  }
  static createElement(t2, i2) {
    const s2 = l.createElement("template");
    return s2.innerHTML = t2, s2;
  }
}
function M(t2, i2, s2 = t2, e2) {
  if (i2 === E) return i2;
  let h2 = void 0 !== e2 ? s2._$Co?.[e2] : s2._$Cl;
  const o2 = a(i2) ? void 0 : i2._$litDirective$;
  return h2?.constructor !== o2 && (h2?._$AO?.(false), void 0 === o2 ? h2 = void 0 : (h2 = new o2(t2), h2._$AT(t2, s2, e2)), void 0 !== e2 ? (s2._$Co ?? (s2._$Co = []))[e2] = h2 : s2._$Cl = h2), void 0 !== h2 && (i2 = M(t2, h2._$AS(t2, i2.values), h2, e2)), i2;
}
class R {
  constructor(t2, i2) {
    this._$AV = [], this._$AN = void 0, this._$AD = t2, this._$AM = i2;
  }
  get parentNode() {
    return this._$AM.parentNode;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  u(t2) {
    const { el: { content: i2 }, parts: s2 } = this._$AD, e2 = (t2?.creationScope ?? l).importNode(i2, true);
    P.currentNode = e2;
    let h2 = P.nextNode(), o2 = 0, n3 = 0, r2 = s2[0];
    for (; void 0 !== r2; ) {
      if (o2 === r2.index) {
        let i3;
        2 === r2.type ? i3 = new k(h2, h2.nextSibling, this, t2) : 1 === r2.type ? i3 = new r2.ctor(h2, r2.name, r2.strings, this, t2) : 6 === r2.type && (i3 = new Z(h2, this, t2)), this._$AV.push(i3), r2 = s2[++n3];
      }
      o2 !== r2?.index && (h2 = P.nextNode(), o2++);
    }
    return P.currentNode = l, e2;
  }
  p(t2) {
    let i2 = 0;
    for (const s2 of this._$AV) void 0 !== s2 && (void 0 !== s2.strings ? (s2._$AI(t2, s2, i2), i2 += s2.strings.length - 2) : s2._$AI(t2[i2])), i2++;
  }
}
class k {
  get _$AU() {
    return this._$AM?._$AU ?? this._$Cv;
  }
  constructor(t2, i2, s2, e2) {
    this.type = 2, this._$AH = A, this._$AN = void 0, this._$AA = t2, this._$AB = i2, this._$AM = s2, this.options = e2, this._$Cv = e2?.isConnected ?? true;
  }
  get parentNode() {
    let t2 = this._$AA.parentNode;
    const i2 = this._$AM;
    return void 0 !== i2 && 11 === t2?.nodeType && (t2 = i2.parentNode), t2;
  }
  get startNode() {
    return this._$AA;
  }
  get endNode() {
    return this._$AB;
  }
  _$AI(t2, i2 = this) {
    t2 = M(this, t2, i2), a(t2) ? t2 === A || null == t2 || "" === t2 ? (this._$AH !== A && this._$AR(), this._$AH = A) : t2 !== this._$AH && t2 !== E && this._(t2) : void 0 !== t2._$litType$ ? this.$(t2) : void 0 !== t2.nodeType ? this.T(t2) : d(t2) ? this.k(t2) : this._(t2);
  }
  O(t2) {
    return this._$AA.parentNode.insertBefore(t2, this._$AB);
  }
  T(t2) {
    this._$AH !== t2 && (this._$AR(), this._$AH = this.O(t2));
  }
  _(t2) {
    this._$AH !== A && a(this._$AH) ? this._$AA.nextSibling.data = t2 : this.T(l.createTextNode(t2)), this._$AH = t2;
  }
  $(t2) {
    const { values: i2, _$litType$: s2 } = t2, e2 = "number" == typeof s2 ? this._$AC(t2) : (void 0 === s2.el && (s2.el = S.createElement(V(s2.h, s2.h[0]), this.options)), s2);
    if (this._$AH?._$AD === e2) this._$AH.p(i2);
    else {
      const t3 = new R(e2, this), s3 = t3.u(this.options);
      t3.p(i2), this.T(s3), this._$AH = t3;
    }
  }
  _$AC(t2) {
    let i2 = C.get(t2.strings);
    return void 0 === i2 && C.set(t2.strings, i2 = new S(t2)), i2;
  }
  k(t2) {
    u(this._$AH) || (this._$AH = [], this._$AR());
    const i2 = this._$AH;
    let s2, e2 = 0;
    for (const h2 of t2) e2 === i2.length ? i2.push(s2 = new k(this.O(c()), this.O(c()), this, this.options)) : s2 = i2[e2], s2._$AI(h2), e2++;
    e2 < i2.length && (this._$AR(s2 && s2._$AB.nextSibling, e2), i2.length = e2);
  }
  _$AR(t2 = this._$AA.nextSibling, s2) {
    for (this._$AP?.(false, true, s2); t2 !== this._$AB; ) {
      const s3 = i$1(t2).nextSibling;
      i$1(t2).remove(), t2 = s3;
    }
  }
  setConnected(t2) {
    void 0 === this._$AM && (this._$Cv = t2, this._$AP?.(t2));
  }
}
class H {
  get tagName() {
    return this.element.tagName;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  constructor(t2, i2, s2, e2, h2) {
    this.type = 1, this._$AH = A, this._$AN = void 0, this.element = t2, this.name = i2, this._$AM = e2, this.options = h2, s2.length > 2 || "" !== s2[0] || "" !== s2[1] ? (this._$AH = Array(s2.length - 1).fill(new String()), this.strings = s2) : this._$AH = A;
  }
  _$AI(t2, i2 = this, s2, e2) {
    const h2 = this.strings;
    let o2 = false;
    if (void 0 === h2) t2 = M(this, t2, i2, 0), o2 = !a(t2) || t2 !== this._$AH && t2 !== E, o2 && (this._$AH = t2);
    else {
      const e3 = t2;
      let n3, r2;
      for (t2 = h2[0], n3 = 0; n3 < h2.length - 1; n3++) r2 = M(this, e3[s2 + n3], i2, n3), r2 === E && (r2 = this._$AH[n3]), o2 || (o2 = !a(r2) || r2 !== this._$AH[n3]), r2 === A ? t2 = A : t2 !== A && (t2 += (r2 ?? "") + h2[n3 + 1]), this._$AH[n3] = r2;
    }
    o2 && !e2 && this.j(t2);
  }
  j(t2) {
    t2 === A ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, t2 ?? "");
  }
}
class I extends H {
  constructor() {
    super(...arguments), this.type = 3;
  }
  j(t2) {
    this.element[this.name] = t2 === A ? void 0 : t2;
  }
}
class L extends H {
  constructor() {
    super(...arguments), this.type = 4;
  }
  j(t2) {
    this.element.toggleAttribute(this.name, !!t2 && t2 !== A);
  }
}
class z extends H {
  constructor(t2, i2, s2, e2, h2) {
    super(t2, i2, s2, e2, h2), this.type = 5;
  }
  _$AI(t2, i2 = this) {
    if ((t2 = M(this, t2, i2, 0) ?? A) === E) return;
    const s2 = this._$AH, e2 = t2 === A && s2 !== A || t2.capture !== s2.capture || t2.once !== s2.once || t2.passive !== s2.passive, h2 = t2 !== A && (s2 === A || e2);
    e2 && this.element.removeEventListener(this.name, this, s2), h2 && this.element.addEventListener(this.name, this, t2), this._$AH = t2;
  }
  handleEvent(t2) {
    "function" == typeof this._$AH ? this._$AH.call(this.options?.host ?? this.element, t2) : this._$AH.handleEvent(t2);
  }
}
class Z {
  constructor(t2, i2, s2) {
    this.element = t2, this.type = 6, this._$AN = void 0, this._$AM = i2, this.options = s2;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(t2) {
    M(this, t2);
  }
}
const B = t$1.litHtmlPolyfillSupport;
B?.(S, k), (t$1.litHtmlVersions ?? (t$1.litHtmlVersions = [])).push("3.3.2");
const D = (t2, i2, s2) => {
  const e2 = s2?.renderBefore ?? i2;
  let h2 = e2._$litPart$;
  if (void 0 === h2) {
    const t3 = s2?.renderBefore ?? null;
    e2._$litPart$ = h2 = new k(i2.insertBefore(c(), t3), t3, void 0, s2 ?? {});
  }
  return h2._$AI(t2), h2;
};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const s = globalThis;
class i extends y$1 {
  constructor() {
    super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
  }
  createRenderRoot() {
    var _a;
    const t2 = super.createRenderRoot();
    return (_a = this.renderOptions).renderBefore ?? (_a.renderBefore = t2.firstChild), t2;
  }
  update(t2) {
    const r2 = this.render();
    this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(t2), this._$Do = D(r2, this.renderRoot, this.renderOptions);
  }
  connectedCallback() {
    super.connectedCallback(), this._$Do?.setConnected(true);
  }
  disconnectedCallback() {
    super.disconnectedCallback(), this._$Do?.setConnected(false);
  }
  render() {
    return E;
  }
}
i._$litElement$ = true, i["finalized"] = true, s.litElementHydrateSupport?.({ LitElement: i });
const o$1 = s.litElementPolyfillSupport;
o$1?.({ LitElement: i });
(s.litElementVersions ?? (s.litElementVersions = [])).push("4.2.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const t = (t2) => (e2, o2) => {
  void 0 !== o2 ? o2.addInitializer(() => {
    customElements.define(t2, e2);
  }) : customElements.define(t2, e2);
};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const o = { attribute: true, type: String, converter: u$1, reflect: false, hasChanged: f$1 }, r$1 = (t2 = o, e2, r2) => {
  const { kind: n3, metadata: i2 } = r2;
  let s2 = globalThis.litPropertyMetadata.get(i2);
  if (void 0 === s2 && globalThis.litPropertyMetadata.set(i2, s2 = /* @__PURE__ */ new Map()), "setter" === n3 && ((t2 = Object.create(t2)).wrapped = true), s2.set(r2.name, t2), "accessor" === n3) {
    const { name: o2 } = r2;
    return { set(r3) {
      const n4 = e2.get.call(this);
      e2.set.call(this, r3), this.requestUpdate(o2, n4, t2, true, r3);
    }, init(e3) {
      return void 0 !== e3 && this.C(o2, void 0, t2, e3), e3;
    } };
  }
  if ("setter" === n3) {
    const { name: o2 } = r2;
    return function(r3) {
      const n4 = this[o2];
      e2.call(this, r3), this.requestUpdate(o2, n4, t2, true, r3);
    };
  }
  throw Error("Unsupported decorator location: " + n3);
};
function n2(t2) {
  return (e2, o2) => "object" == typeof o2 ? r$1(t2, e2, o2) : ((t3, e3, o3) => {
    const r2 = e3.hasOwnProperty(o3);
    return e3.constructor.createProperty(o3, t3), r2 ? Object.getOwnPropertyDescriptor(e3, o3) : void 0;
  })(t2, e2, o2);
}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
function r(r2) {
  return n2({ ...r2, state: true, attribute: false });
}
var __defProp$1 = Object.defineProperty;
var __getOwnPropDesc$1 = Object.getOwnPropertyDescriptor;
var __decorateClass$1 = (decorators, target, key, kind) => {
  var result = kind > 1 ? void 0 : kind ? __getOwnPropDesc$1(target, key) : target;
  for (var i2 = decorators.length - 1, decorator; i2 >= 0; i2--)
    if (decorator = decorators[i2])
      result = (kind ? decorator(target, key, result) : decorator(result)) || result;
  if (kind && result) __defProp$1(target, key, result);
  return result;
};
let ProportionalLightPanel = class extends i {
  constructor() {
    super(...arguments);
    this.narrow = false;
    this.route = null;
    this._entries = [];
    this._loading = true;
    this._error = null;
    this._editingEntryId = null;
  }
  // -------------------------------------------------------------------------
  // Lifecycle
  // -------------------------------------------------------------------------
  connectedCallback() {
    super.connectedCallback();
    this._loadEntries();
  }
  // -------------------------------------------------------------------------
  // Data loading
  // -------------------------------------------------------------------------
  async _loadEntries() {
    this._loading = true;
    this._error = null;
    try {
      const entries = await this.hass.callWS({
        type: "config_entries/get",
        domain: "proportional_light"
      });
      this._entries = entries;
    } catch (err) {
      this._error = String(err);
    } finally {
      this._loading = false;
    }
  }
  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  render() {
    return b`
      <hass-subpage
        .hass=${this.hass}
        .narrow=${this.narrow}
        header="Proportional Light Groups"
      >
        <ha-fab
          slot="fab"
          label="Add group"
          extended
          @click=${this._handleAdd}
        >
          <ha-icon slot="icon" icon="mdi:plus"></ha-icon>
        </ha-fab>

        <div class="content">
          ${this._loading ? b`<div class="loading">
                <ha-circular-progress active></ha-circular-progress>
              </div>` : this._error ? b`<ha-alert alert-type="error">${this._error}</ha-alert>` : this._entries.length === 0 ? b`<div class="empty">
                <p>No proportional light groups configured yet.</p>
                <p>Click + to create your first group.</p>
              </div>` : this._renderEntries()}
        </div>
      </hass-subpage>
    `;
  }
  _renderEntries() {
    return b`
      ${this._entries.map(
      (entry) => b`
          <ha-card
            class="entry-card"
            .header=${entry.title || entry.data.name || "Unnamed Group"}
          >
            <div class="card-content">
              <div class="selector-badge">
                <ha-icon icon=${this._selectorIcon(entry.data.selector_type)}></ha-icon>
                <span>${this._selectorLabel(entry.data.selector_type, entry.data.selector_value)}</span>
              </div>
              <div class="entry-state state-${entry.state}">${entry.state}</div>
            </div>
            <div class="card-actions">
              <ha-button @click=${() => this._handleEdit(entry)}>
                Configure
              </ha-button>
              <ha-button
                class="danger"
                @click=${() => this._handleDelete(entry)}
              >
                Remove
              </ha-button>
            </div>
          </ha-card>
        `
    )}
    `;
  }
  // -------------------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------------------
  _selectorIcon(type) {
    switch (type) {
      case "area":
        return "mdi:floor-plan";
      case "device":
        return "mdi:chip";
      default:
        return "mdi:lightbulb-multiple";
    }
  }
  _selectorLabel(type, value) {
    if (!value) return "—";
    switch (type) {
      case "area":
        return `Area: ${value}`;
      case "device":
        return `Device: ${value}`;
      default: {
        const list = Array.isArray(value) ? value : [value];
        return `${list.length} light${list.length !== 1 ? "s" : ""}`;
      }
    }
  }
  // -------------------------------------------------------------------------
  // Event handlers
  // -------------------------------------------------------------------------
  _handleEdit(entry) {
    this._editingEntryId = entry.entry_id;
    this.dispatchEvent(
      new CustomEvent("edit-entry", { detail: { entry }, bubbles: true, composed: true })
    );
  }
  _handleAdd() {
    this.dispatchEvent(
      new CustomEvent("add-entry", { bubbles: true, composed: true })
    );
  }
  async _handleDelete(entry) {
    if (!confirm(`Remove "${entry.title}"? This cannot be undone.`)) return;
    try {
      await this.hass.callWS({ type: "config_entries/delete", entry_id: entry.entry_id });
      await this._loadEntries();
    } catch (err) {
      alert(`Failed to remove entry: ${err}`);
    }
  }
};
ProportionalLightPanel.styles = i$3`
    :host {
      display: block;
    }
    .content {
      padding: 16px;
      max-width: 900px;
      margin: 0 auto;
    }
    .loading,
    .empty {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 48px 16px;
      color: var(--secondary-text-color);
      text-align: center;
    }
    ha-card.entry-card {
      margin-bottom: 16px;
    }
    .card-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px 16px;
    }
    .selector-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--secondary-text-color);
      font-size: 0.9rem;
    }
    .entry-state {
      font-size: 0.75rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 2px 8px;
      border-radius: 12px;
      background: var(--divider-color);
    }
    .entry-state.state-loaded {
      background: var(--success-color);
      color: #fff;
    }
    .entry-state.state-not_loaded,
    .entry-state.state-failed_unload {
      background: var(--error-color);
      color: #fff;
    }
    .card-actions {
      display: flex;
      justify-content: flex-end;
      padding: 8px 8px 8px;
      gap: 8px;
    }
    ha-button.danger {
      --mdc-theme-primary: var(--error-color);
    }
  `;
__decorateClass$1([
  n2({ attribute: false })
], ProportionalLightPanel.prototype, "hass", 2);
__decorateClass$1([
  n2({ type: Boolean })
], ProportionalLightPanel.prototype, "narrow", 2);
__decorateClass$1([
  n2({ attribute: false })
], ProportionalLightPanel.prototype, "route", 2);
__decorateClass$1([
  r()
], ProportionalLightPanel.prototype, "_entries", 2);
__decorateClass$1([
  r()
], ProportionalLightPanel.prototype, "_loading", 2);
__decorateClass$1([
  r()
], ProportionalLightPanel.prototype, "_error", 2);
__decorateClass$1([
  r()
], ProportionalLightPanel.prototype, "_editingEntryId", 2);
ProportionalLightPanel = __decorateClass$1([
  t("proportional-light-panel")
], ProportionalLightPanel);
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __decorateClass = (decorators, target, key, kind) => {
  var result = kind > 1 ? void 0 : kind ? __getOwnPropDesc(target, key) : target;
  for (var i2 = decorators.length - 1, decorator; i2 >= 0; i2--)
    if (decorator = decorators[i2])
      result = (kind ? decorator(target, key, result) : decorator(result)) || result;
  if (kind && result) __defProp(target, key, result);
  return result;
};
let ProportionalLightEntryEditor = class extends i {
  constructor() {
    super(...arguments);
    this._name = "";
    this._selectorType = "entities";
    this._selectorValue = null;
    this._entityProps = {};
    this._proportionResetMode = "on_specific_brightness";
    this._proportionResetTimeout = 28800;
    this._resolvedEntities = [];
    this._resolving = false;
    this._saving = false;
  }
  // -------------------------------------------------------------------------
  // Lifecycle
  // -------------------------------------------------------------------------
  willUpdate(changed) {
    if (changed.has("entry") && this.entry) {
      const d2 = { ...this.entry.data, ...this.entry.options };
      this._name = d2.name ?? this.entry.title ?? "";
      this._selectorType = d2.selector_type ?? "entities";
      this._selectorValue = d2.selector_value ?? [];
      this._entityProps = d2.entity_props ?? {};
      this._proportionResetMode = d2.proportion_reset_mode ?? "on_specific_brightness";
      this._proportionResetTimeout = d2.proportion_reset_timeout ?? 28800;
      if (this._selectorValue) this._resolveEntities();
    }
  }
  // -------------------------------------------------------------------------
  // Entity resolution
  // -------------------------------------------------------------------------
  async _resolveEntities() {
    if (!this.entry || !this._selectorValue) {
      this._resolvedEntities = [];
      return;
    }
    this._resolving = true;
    try {
      const resp = await this.hass.callWS({
        type: "proportional_light/get_resolved_entities",
        entry_id: this.entry.entry_id
      });
      this._resolvedEntities = resp.entities;
    } catch {
      this._resolvedEntities = [];
    } finally {
      this._resolving = false;
    }
  }
  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  render() {
    return b`
      <ha-card header=${this.entry ? "Edit Group" : "New Group"}>
        <div class="card-content">
          <!-- Name -->
          <ha-textfield
            label="Group name"
            .value=${this._name}
            @input=${(e2) => this._name = e2.target.value}
          ></ha-textfield>

          <!-- Selector type -->
          <div class="section-label">Entity source</div>
          <ha-select
            label="Source type"
            .value=${this._selectorType}
            @selected=${this._handleSelectorTypeChange}
            @closed=${(e2) => e2.stopPropagation()}
          >
            <ha-list-item value="entities">Specific lights</ha-list-item>
            <ha-list-item value="area">Area</ha-list-item>
            <ha-list-item value="device">Device</ha-list-item>
          </ha-select>

          <!-- Dynamic HA selector — changes based on selected type -->
          <ha-selector
            .hass=${this.hass}
            .selector=${this._buildSelectorConfig()}
            .value=${this._selectorValue ?? (this._selectorType === "entities" ? [] : "")}
            .label=${"Select " + this._selectorType}
            @value-changed=${this._handleSelectorValueChange}
          ></ha-selector>

          <!-- Resolved entity list with per-light overrides -->
          ${this._resolvedEntities.length > 0 ? b`
                <div class="section-label">
                  Per-light settings
                  ${this._resolving ? b`<ha-circular-progress active size="small"></ha-circular-progress>` : A}
                </div>
                ${this._renderEntityProps()}
              ` : this._resolving ? b`<ha-circular-progress active></ha-circular-progress>` : A}

          <!-- Proportion reset -->
          <div class="section-label">Proportion reset</div>
          <ha-selector
            .hass=${this.hass}
            .selector=${{
      select: {
        options: [
          { value: "never", label: "Never" },
          { value: "on_off", label: "On turn-off" },
          { value: "on_specific_brightness", label: "When turned on with explicit brightness" },
          { value: "on_off_and_specific", label: "Both of the above" }
        ]
      }
    }}
            .value=${this._proportionResetMode}
            label="Reset mode"
            @value-changed=${(e2) => this._proportionResetMode = e2.detail.value}
          ></ha-selector>

          <ha-selector
            .hass=${this.hass}
            .selector=${{
      number: { min: 0, max: 86400, step: 300, mode: "box", unit_of_measurement: "s" }
    }}
            .value=${this._proportionResetTimeout}
            label="Reset timeout"
            @value-changed=${(e2) => this._proportionResetTimeout = Number(e2.detail.value)}
          ></ha-selector>
        </div>

        <div class="card-actions">
          <ha-button @click=${this._handleCancel}>Cancel</ha-button>
          <ha-button
            raised
            .disabled=${this._saving}
            @click=${this._handleSave}
          >
            ${this._saving ? "Saving…" : "Save"}
          </ha-button>
        </div>
      </ha-card>
    `;
  }
  _renderEntityProps() {
    return b`
      <div class="entity-list">
        ${this._resolvedEntities.map((entityId) => {
      const props = this._entityProps[entityId] ?? {};
      const state2 = this.hass.states[entityId];
      const label = state2?.attributes?.friendly_name ?? entityId;
      const isColorable = this._isColorable(entityId);
      return b`
            <ha-card outlined class="entity-row">
              <div class="entity-row-content">
                <state-badge
                  .hass=${this.hass}
                  .stateObj=${state2}
                ></state-badge>
                <div class="entity-info">
                  <div class="entity-name">${label}</div>
                  <div class="entity-id">${entityId}</div>
                </div>
                <div class="entity-controls">
                  <ha-selector
                    .hass=${this.hass}
                    .selector=${{ number: { min: 0, max: 100, step: 1, mode: "slider", unit_of_measurement: "%" } }}
                    .value=${(props.default_proportion ?? 1) * 100}
                    label="Default proportion"
                    @value-changed=${(e2) => this._updateEntityProp(entityId, "default_proportion", Number(e2.detail.value) / 100)}
                  ></ha-selector>
                  ${isColorable ? b`
                        <ha-selector
                          .hass=${this.hass}
                          .selector=${{ number: { min: -180, max: 180, step: 1, mode: "box", unit_of_measurement: "°" } }}
                          .value=${props.hue_offset ?? 0}
                          label="Hue offset"
                          @value-changed=${(e2) => this._updateEntityProp(entityId, "hue_offset", Number(e2.detail.value))}
                        ></ha-selector>
                      ` : A}
                </div>
              </div>
            </ha-card>
          `;
    })}
      </div>
    `;
  }
  // -------------------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------------------
  _buildSelectorConfig() {
    switch (this._selectorType) {
      case "area":
        return { area: {} };
      case "device":
        return { device: {} };
      default:
        return { entity: { domain: "light", multiple: true } };
    }
  }
  _isColorable(entityId) {
    const state2 = this.hass.states[entityId];
    if (!state2) return false;
    const modes = state2.attributes.supported_color_modes ?? [];
    return modes.some((m2) => ["hs", "xy", "rgb", "rgbw", "rgbww"].includes(m2));
  }
  _updateEntityProp(entityId, key, value) {
    this._entityProps = {
      ...this._entityProps,
      [entityId]: { ...this._entityProps[entityId], [key]: value }
    };
  }
  // -------------------------------------------------------------------------
  // Event handlers
  // -------------------------------------------------------------------------
  _handleSelectorTypeChange(e2) {
    const newType = e2.target.value;
    if (newType === this._selectorType) return;
    this._selectorType = newType;
    this._selectorValue = newType === "entities" ? [] : "";
    this._resolvedEntities = [];
  }
  _handleSelectorValueChange(e2) {
    this._selectorValue = e2.detail.value;
    if (this._selectorValue && (Array.isArray(this._selectorValue) ? this._selectorValue.length > 0 : true)) {
      this._resolveEntities();
    }
  }
  async _handleSave() {
    if (!this._name.trim()) {
      alert("Please enter a name for the group.");
      return;
    }
    if (!this._selectorValue || Array.isArray(this._selectorValue) && this._selectorValue.length === 0) {
      alert("Please select at least one entity source.");
      return;
    }
    this._saving = true;
    try {
      const data = {
        name: this._name.trim(),
        selector_type: this._selectorType,
        selector_value: this._selectorValue,
        entity_props: this._entityProps,
        proportion_reset_mode: this._proportionResetMode,
        proportion_reset_timeout: this._proportionResetTimeout
      };
      if (this.entry) {
        await this.hass.callWS({
          type: "proportional_light/update_entry",
          entry_id: this.entry.entry_id,
          data
        });
      }
      this.dispatchEvent(new CustomEvent("save", { detail: { data }, bubbles: true, composed: true }));
    } catch (err) {
      alert(`Save failed: ${err}`);
    } finally {
      this._saving = false;
    }
  }
  _handleCancel() {
    this.dispatchEvent(new CustomEvent("cancel", { bubbles: true, composed: true }));
  }
};
ProportionalLightEntryEditor.styles = i$3`
    :host {
      display: block;
    }
    .card-content {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 16px;
    }
    .section-label {
      font-size: 0.85rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--secondary-text-color);
      margin-top: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    ha-textfield,
    ha-select,
    ha-selector {
      width: 100%;
    }
    .entity-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    ha-card.entity-row {
      --ha-card-border-radius: 8px;
    }
    .entity-row-content {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 12px;
    }
    .entity-info {
      flex: 0 0 auto;
      min-width: 160px;
    }
    .entity-name {
      font-weight: 500;
    }
    .entity-id {
      font-size: 0.8rem;
      color: var(--secondary-text-color);
    }
    .entity-controls {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .card-actions {
      display: flex;
      justify-content: flex-end;
      padding: 8px;
      gap: 8px;
      border-top: 1px solid var(--divider-color);
    }
  `;
__decorateClass([
  n2({ attribute: false })
], ProportionalLightEntryEditor.prototype, "hass", 2);
__decorateClass([
  n2({ attribute: false })
], ProportionalLightEntryEditor.prototype, "entry", 2);
__decorateClass([
  r()
], ProportionalLightEntryEditor.prototype, "_name", 2);
__decorateClass([
  r()
], ProportionalLightEntryEditor.prototype, "_selectorType", 2);
__decorateClass([
  r()
], ProportionalLightEntryEditor.prototype, "_selectorValue", 2);
__decorateClass([
  r()
], ProportionalLightEntryEditor.prototype, "_entityProps", 2);
__decorateClass([
  r()
], ProportionalLightEntryEditor.prototype, "_proportionResetMode", 2);
__decorateClass([
  r()
], ProportionalLightEntryEditor.prototype, "_proportionResetTimeout", 2);
__decorateClass([
  r()
], ProportionalLightEntryEditor.prototype, "_resolvedEntities", 2);
__decorateClass([
  r()
], ProportionalLightEntryEditor.prototype, "_resolving", 2);
__decorateClass([
  r()
], ProportionalLightEntryEditor.prototype, "_saving", 2);
ProportionalLightEntryEditor = __decorateClass([
  t("proportional-light-entry-editor")
], ProportionalLightEntryEditor);
console.info(
  "%c PROPORTIONAL-LIGHT %c panel loaded",
  "background:#1565c0;color:#fff;padding:2px 6px;border-radius:3px 0 0 3px;font-weight:bold",
  "background:#333;color:#1565c0;padding:2px 6px;border-radius:0 3px 3px 0"
);
