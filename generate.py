#!/usr/bin/env python3
"""
J&M Construction Services — Website Generator
Reads business_config.json, calls Claude API for copy, writes output/index.html
Usage: python generate.py [config_path]
"""

import html
import json
import os
import re
import sys

import anthropic

# ── HTML TEMPLATE ──────────────────────────────────────────────────────────────
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{PAGE_TITLE}}</title>
  <meta name="description" content="{{META_DESC}}">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    :root {
      --primary: {{PRIMARY_COLOR}};
      --accent:  {{ACCENT_COLOR}};
      --dark:    {{DARK_COLOR}};
      --light:   {{LIGHT_BG}};
      --white:   #ffffff;
      --radius:  8px;
      --shadow:  0 4px 24px rgba(0,0,0,0.10);
      --max-w:   1200px;
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      color: var(--dark);
      line-height: 1.6;
      font-size: 16px;
    }

    .container {
      max-width: var(--max-w);
      margin: 0 auto;
      padding: 0 1.5rem;
    }

    /* ── HEADER ── */
    .site-header {
      position: sticky;
      top: 0;
      z-index: 100;
      background: var(--white);
      box-shadow: 0 2px 12px rgba(0,0,0,0.10);
    }
    .site-header .container {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 0.875rem;
      padding-bottom: 0.875rem;
    }
    .logo {
      display: flex;
      flex-direction: column;
      line-height: 1.1;
    }
    .logo-main {
      font-size: 1.4rem;
      font-weight: 900;
      color: var(--primary);
      letter-spacing: -0.02em;
    }
    .logo-main em {
      font-style: normal;
      color: var(--accent);
    }
    .logo-sub {
      font-size: 0.6rem;
      font-weight: 700;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--primary);
      opacity: 0.65;
    }
    .header-right {
      display: flex;
      align-items: center;
      gap: 2rem;
    }
    .nav-links {
      display: flex;
      gap: 1.75rem;
      list-style: none;
    }
    .nav-links a {
      text-decoration: none;
      color: var(--dark);
      font-weight: 500;
      font-size: 0.9375rem;
      transition: color 0.2s;
    }
    .nav-links a:hover { color: var(--primary); }
    .header-phone {
      font-size: 1.0625rem;
      font-weight: 800;
      color: var(--accent);
      text-decoration: none;
      white-space: nowrap;
    }
    .header-phone:hover { opacity: 0.85; }

    /* ── BUTTONS ── */
    .btn {
      display: inline-block;
      padding: 1rem 2.5rem;
      border-radius: 50px;
      font-size: 1.0625rem;
      font-weight: 700;
      text-decoration: none;
      transition: transform 0.2s, box-shadow 0.2s;
      cursor: pointer;
      border: none;
      font-family: inherit;
      letter-spacing: 0.01em;
    }
    .btn-accent {
      background: var(--accent);
      color: var(--dark);
      box-shadow: 0 4px 20px rgba(212,168,67,0.35);
    }
    .btn-accent:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 28px rgba(212,168,67,0.50);
    }
    .btn-full {
      width: 100%;
      text-align: center;
      padding: 1rem;
      border-radius: var(--radius);
    }

    /* ── HERO ── */
    #hero {
      min-height: 100vh;
      background: linear-gradient(140deg, var(--dark) 0%, var(--primary) 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 7rem 1.5rem 5rem;
      position: relative;
      overflow: hidden;
    }
    #hero::before {
      content: '';
      position: absolute;
      inset: 0;
      background-image: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 60px,
        rgba(255,255,255,0.02) 60px,
        rgba(255,255,255,0.02) 61px
      ),
      repeating-linear-gradient(
        90deg,
        transparent,
        transparent 60px,
        rgba(255,255,255,0.02) 60px,
        rgba(255,255,255,0.02) 61px
      );
    }
    .hero-inner {
      position: relative;
      max-width: 820px;
    }
    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(212,168,67,0.15);
      border: 1px solid rgba(212,168,67,0.45);
      color: var(--accent);
      font-size: 0.8125rem;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      padding: 0.4rem 1.1rem;
      border-radius: 50px;
      margin-bottom: 1.75rem;
    }
    #hero h1 {
      font-size: clamp(2.1rem, 5.5vw, 3.75rem);
      font-weight: 900;
      color: var(--white);
      line-height: 1.1;
      margin-bottom: 1.375rem;
      letter-spacing: -0.025em;
    }
    #hero h1 em {
      font-style: normal;
      color: var(--accent);
    }
    .hero-subtitle {
      font-size: clamp(1rem, 2.5vw, 1.25rem);
      color: rgba(255,255,255,0.80);
      max-width: 620px;
      margin: 0 auto 2.5rem;
      line-height: 1.65;
    }
    .cta-group {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.875rem;
    }
    .cta-subtext {
      color: rgba(255,255,255,0.60);
      font-size: 0.875rem;
    }

    /* ── TRUST BAR ── */
    .trust-bar {
      background: var(--primary);
      padding: 1.125rem 0;
    }
    .trust-bar .container {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 2rem;
    }
    .trust-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: rgba(255,255,255,0.88);
      font-size: 0.9rem;
      font-weight: 500;
    }
    .trust-item .check {
      color: var(--accent);
      font-weight: 900;
      font-size: 1rem;
    }

    /* ── SECTION COMMON ── */
    section { padding: 5rem 0; }
    .section-header {
      text-align: center;
      margin-bottom: 3rem;
    }
    .section-label {
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 0.625rem;
    }
    .section-header h2 {
      font-size: clamp(1.75rem, 3.5vw, 2.5rem);
      font-weight: 800;
      color: var(--primary);
      letter-spacing: -0.02em;
      line-height: 1.2;
    }
    .section-header p {
      margin-top: 0.75rem;
      font-size: 1.0625rem;
      color: #64748b;
      max-width: 560px;
      margin-left: auto;
      margin-right: auto;
    }

    /* ── SERVICES ── */
    #services { background: var(--white); }
    .services-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
    }
    .service-card {
      background: var(--white);
      border: 1.5px solid #e2e8f0;
      border-radius: var(--radius);
      padding: 2rem;
      box-shadow: var(--shadow);
      transition: transform 0.22s, border-color 0.22s, box-shadow 0.22s;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }
    .service-card:hover {
      transform: translateY(-4px);
      border-color: var(--accent);
      box-shadow: 0 10px 36px rgba(0,0,0,0.13);
    }
    .service-icon { font-size: 2.25rem; line-height: 1; }
    .service-card h3 {
      font-size: 1.1875rem;
      font-weight: 700;
      color: var(--primary);
    }
    .service-card p {
      color: #475569;
      font-size: 0.9375rem;
      line-height: 1.65;
      flex: 1;
    }
    .service-highlight {
      margin-top: 0.25rem;
      font-size: 0.775rem;
      font-weight: 700;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.07em;
    }

    /* ── TESTIMONIALS ── */
    #testimonials { background: var(--light); }
    .testimonials-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
      gap: 1.5rem;
    }
    .testimonial-card {
      background: var(--white);
      border-radius: var(--radius);
      padding: 2rem;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      gap: 1rem;
      border-top: 3px solid var(--accent);
    }
    .stars { color: #f59e0b; font-size: 1.125rem; letter-spacing: 3px; }
    .testimonial-card blockquote {
      font-style: italic;
      color: #475569;
      line-height: 1.75;
      font-size: 0.9375rem;
      flex: 1;
    }
    .testimonial-author strong {
      display: block;
      color: var(--dark);
      font-weight: 600;
      font-style: normal;
    }
    .testimonial-author span {
      font-size: 0.875rem;
      color: #64748b;
    }

    /* ── CONTACT ── */
    #contact { background: var(--white); }
    .contact-grid {
      display: grid;
      grid-template-columns: 1fr 1.1fr;
      gap: 4rem;
      align-items: start;
    }
    .contact-info { display: flex; flex-direction: column; gap: 1.75rem; }
    .contact-phone {
      font-size: 2.125rem;
      font-weight: 900;
      color: var(--accent);
      text-decoration: none;
      display: block;
      line-height: 1;
    }
    .contact-phone:hover { opacity: 0.85; }
    .contact-email {
      font-size: 1rem;
      color: var(--primary);
      text-decoration: none;
      font-weight: 500;
    }
    .contact-email:hover { text-decoration: underline; }
    .info-block { display: flex; flex-direction: column; gap: 0.375rem; }
    .info-block h4 {
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.13em;
      text-transform: uppercase;
      color: #94a3b8;
      margin-bottom: 0.25rem;
    }
    .info-block p { font-size: 0.9375rem; color: var(--dark); }
    .hours-table { display: flex; flex-direction: column; }
    .hours-row {
      display: flex;
      justify-content: space-between;
      padding: 0.5rem 0;
      border-bottom: 1px solid #e2e8f0;
      font-size: 0.9rem;
    }
    .hours-row:last-child { border-bottom: none; }
    .hours-row span:first-child { font-weight: 500; color: #475569; }

    /* ── CONTACT FORM ── */
    .contact-form { display: flex; flex-direction: column; gap: 1.25rem; }
    .form-group { display: flex; flex-direction: column; gap: 0.375rem; }
    .form-group label { font-size: 0.875rem; font-weight: 600; color: var(--dark); }
    .form-group input,
    .form-group select,
    .form-group textarea {
      width: 100%;
      border: 1.5px solid #cbd5e1;
      border-radius: var(--radius);
      padding: 0.75rem 1rem;
      font-size: 0.9375rem;
      font-family: inherit;
      color: var(--dark);
      background: var(--white);
      transition: border-color 0.2s, box-shadow 0.2s;
      appearance: none;
    }
    .form-group input:focus,
    .form-group select:focus,
    .form-group textarea:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(27,58,92,0.10);
    }
    .form-group textarea { resize: vertical; min-height: 110px; }
    .form-disclaimer { font-size: 0.75rem; color: #94a3b8; text-align: center; }
    .form-success {
      background: #f0fdf4;
      border: 1.5px solid #86efac;
      border-radius: var(--radius);
      padding: 2.5rem;
      text-align: center;
    }
    .form-success h3 { color: #166534; font-size: 1.25rem; margin-bottom: 0.5rem; }
    .form-success p { color: #166534; }

    /* ── FOOTER ── */
    footer {
      background: var(--dark);
      color: rgba(255,255,255,0.70);
      padding: 4rem 0 0;
    }
    .footer-grid {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr;
      gap: 3rem;
      padding-bottom: 3rem;
    }
    .footer-brand {
      font-size: 1.3rem;
      font-weight: 900;
      color: var(--white);
      margin-bottom: 0.75rem;
    }
    .footer-brand em { font-style: normal; color: var(--accent); }
    .footer-tagline {
      font-size: 0.9375rem;
      color: rgba(255,255,255,0.55);
      line-height: 1.65;
    }
    footer h4 {
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 1rem;
    }
    footer ul { list-style: none; display: flex; flex-direction: column; gap: 0.625rem; }
    footer ul a {
      color: rgba(255,255,255,0.60);
      text-decoration: none;
      font-size: 0.9375rem;
      transition: color 0.2s;
    }
    footer ul a:hover { color: var(--white); }
    footer p { font-size: 0.9375rem; color: rgba(255,255,255,0.60); }
    footer a { color: rgba(255,255,255,0.60); text-decoration: none; transition: color 0.2s; }
    footer a:hover { color: var(--white); }
    .footer-bottom {
      border-top: 1px solid rgba(255,255,255,0.08);
      padding: 1.25rem 0;
      text-align: center;
      font-size: 0.8125rem;
      color: rgba(255,255,255,0.35);
    }

    /* ── RESPONSIVE ── */
    @media (max-width: 768px) {
      .nav-links { display: none; }
      .contact-grid { grid-template-columns: 1fr; gap: 2.5rem; }
      .footer-grid { grid-template-columns: 1fr; gap: 2rem; }
      .trust-bar .container { gap: 1rem 1.5rem; }
      .trust-item { font-size: 0.85rem; }
    }
    @media (max-width: 480px) {
      .header-phone { font-size: 0.9375rem; }
      #hero h1 { font-size: 2rem; }
    }
  </style>
</head>
<body>

<!-- HEADER -->
<header class="site-header">
  <div class="container">
    <div class="logo">
      <span class="logo-main"><em>J&amp;M</em> Construction Services</span>
      <span class="logo-sub">North Texas</span>
    </div>
    <nav class="header-right">
      <ul class="nav-links">
        <li><a href="#services">Services</a></li>
        <li><a href="#testimonials">Reviews</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
      <a href="tel:{{PHONE}}" class="header-phone">&#9742;&nbsp;{{PHONE}}</a>
    </nav>
  </div>
</header>

<!-- HERO -->
<section id="hero">
  <div class="hero-inner">
    <div class="hero-badge">&#9733;&nbsp;Serving North Texas</div>
    <h1>{{HERO_HEADLINE}}</h1>
    <p class="hero-subtitle">{{HERO_SUBTITLE}}</p>
    <div class="cta-group">
      <a href="tel:{{PHONE}}" class="btn btn-accent">{{CTA_TEXT}}</a>
      <span class="cta-subtext">{{CTA_SUBTEXT}}</span>
    </div>
  </div>
</section>

<!-- TRUST BAR -->
<div class="trust-bar">
  <div class="container">
    <div class="trust-item"><span class="check">&#10003;</span> Owner-Operated</div>
    <div class="trust-item"><span class="check">&#10003;</span> Free Estimates</div>
    <div class="trust-item"><span class="check">&#10003;</span> Quality Craftsmanship</div>
    <div class="trust-item"><span class="check">&#10003;</span> North Texas Proud</div>
  </div>
</div>

<!-- SERVICES -->
<section id="services">
  <div class="container">
    <div class="section-header">
      <span class="section-label">What We Do</span>
      <h2>Our Services</h2>
      <p>From demolition to finish work — we handle it all with skill and care.</p>
    </div>
    <div class="services-grid">
      {{SERVICES_HTML}}
    </div>
  </div>
</section>

<!-- TESTIMONIALS -->
<section id="testimonials">
  <div class="container">
    <div class="section-header">
      <span class="section-label">Customer Reviews</span>
      <h2>What Our Customers Say</h2>
    </div>
    <div class="testimonials-grid">
      {{TESTIMONIALS_HTML}}
    </div>
  </div>
</section>

<!-- CONTACT -->
<section id="contact">
  <div class="container">
    <div class="section-header">
      <span class="section-label">Get In Touch</span>
      <h2>{{CONTACT_HEADLINE}}</h2>
      <p>{{CONTACT_SUBTEXT}}</p>
    </div>
    <div class="contact-grid">
      <div class="contact-info">
        <div>
          <a href="tel:{{PHONE}}" class="contact-phone">&#9742;&nbsp;{{PHONE}}</a>
        </div>
        <div>
          <a href="mailto:{{EMAIL}}" class="contact-email">{{EMAIL}}</a>
        </div>
        <div class="info-block">
          <h4>Service Area</h4>
          <p>{{SERVICE_AREA}}</p>
        </div>
        <div class="info-block">
          <h4>Business Hours</h4>
          <div class="hours-table">
            <div class="hours-row"><span>Mon &ndash; Fri</span><span>{{HOURS_WEEKDAY}}</span></div>
            <div class="hours-row"><span>Saturday</span><span>{{HOURS_SAT}}</span></div>
            <div class="hours-row"><span>Sunday</span><span>{{HOURS_SUN}}</span></div>
          </div>
        </div>
      </div>
      <form class="contact-form" id="contact-form" novalidate>
        <div class="form-group">
          <label for="fname">Your Name</label>
          <input type="text" id="fname" name="name" required placeholder="Jane Smith">
        </div>
        <div class="form-group">
          <label for="fphone">Phone Number</label>
          <input type="tel" id="fphone" name="phone" required placeholder="(682) 000-0000">
        </div>
        <div class="form-group">
          <label for="fservice">Service Needed</label>
          <select id="fservice" name="service">
            {{SERVICE_OPTIONS_HTML}}
          </select>
        </div>
        <div class="form-group">
          <label for="fmessage">Describe Your Project</label>
          <textarea id="fmessage" name="message" rows="4" placeholder="Tell us a bit about what you need..."></textarea>
        </div>
        <button type="submit" class="btn btn-accent btn-full">Send My Request</button>
        <p class="form-disclaimer">{{FORM_DISCLAIMER}}</p>
      </form>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div class="container footer-grid">
    <div>
      <div class="footer-brand"><em>J&amp;M</em> Construction Services</div>
      <p class="footer-tagline">{{FOOTER_TAGLINE}}</p>
    </div>
    <div>
      <h4>Quick Links</h4>
      <ul>
        <li><a href="#services">Services</a></li>
        <li><a href="#testimonials">Reviews</a></li>
        <li><a href="#contact">Get a Quote</a></li>
      </ul>
    </div>
    <div>
      <h4>Contact</h4>
      <p><a href="tel:{{PHONE}}">{{PHONE}}</a></p>
      <p><a href="mailto:{{EMAIL}}">{{EMAIL}}</a></p>
      <p style="margin-top:0.5rem;">{{SERVICE_AREA}}</p>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="container">
      <p>&copy; 2026 J&amp;M Construction Services &mdash; {{SERVICE_AREA}}</p>
    </div>
  </div>
</footer>

<script>
  document.querySelectorAll('a[href^="#"]').forEach(function(a) {
    a.addEventListener('click', function(e) {
      var target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      var phoneVal = document.getElementById('fphone') ? document.getElementById('fphone').value : '';
      this.innerHTML =
        '<div class="form-success">' +
        '<h3>&#10003; Request Received!</h3>' +
        '<p>Thank you! Julius will be in touch shortly' +
        (phoneVal ? ' at ' + phoneVal : '') + '.</p>' +
        '</div>';
    });
  }
</script>
</body>
</html>
"""


# ── CONFIG ─────────────────────────────────────────────────────────────────────

def load_config(path: str) -> dict:
    required = ["business", "contact", "services", "theme", "hours", "meta"]
    try:
        with open(path, encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"Config file not found: {path}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON in config: {e}")

    missing = [k for k in required if k not in config]
    if missing:
        raise SystemExit(f"Config missing required keys: {', '.join(missing)}")
    return config


# ── PROMPT BUILDER ─────────────────────────────────────────────────────────────

def build_claude_prompt(config: dict) -> str:
    b = config["business"]
    c = config["contact"]
    num_services = len(config["services"])

    services_text = "\n".join(
        f"  - {s['name']} (keywords: {', '.join(s.get('keywords', []))})"
        for s in config["services"]
    )
    diff_text = "\n".join(f"  - {d}" for d in config.get("differentiators", []))

    return f"""You are a professional copywriter specializing in local construction and home service business websites.

Generate website copy for this business. Return ONLY valid JSON — no markdown fences, no explanation.

BUSINESS DETAILS:
- Business Name: {b["name"]}
- Business Type: {b.get("type", "construction services")}
- Owner: {b.get("owner_name", "")}
- Service Area: {c.get("service_area", "")}
- Key Differentiators:
{diff_text}
- Services Offered:
{services_text}

COPY INSTRUCTIONS:
- Write in second person addressing the homeowner ("your project", "your property")
- Headlines must be benefit-driven and specific to construction services in North Texas
- Every service description is exactly 2 sentences: sentence 1 names the problem it solves, sentence 2 states why J&M Construction Services is the right choice
- Each testimonial must sound authentic — include a specific job detail (e.g. a room, a material, a timeline)
- Do not invent credentials or license numbers not provided
- Tone: professional, trustworthy, straightforward — like a respected local contractor
- No exclamation marks in headlines or the hero subtitle

Return this exact JSON structure:

{{
  "hero": {{
    "headline": "string (max 10 words, benefit-driven, no exclamation marks)",
    "subtitle": "string (1 sentence, 20-35 words, mentions North Texas, expands on headline)",
    "cta_text": "string (button label, 3-5 words, starts with action verb: Get, Call, or Request)",
    "cta_subtext": "string (under the button, max 9 words, urgency or reassurance)"
  }},
  "services": [
    {{
      "name": "string (service name exactly as listed)",
      "icon": "string (one relevant emoji)",
      "description": "string (exactly 2 sentences as described)",
      "highlight": "string (benefit phrase, max 6 words)"
    }}
  ],
  "testimonials": [
    {{
      "quote": "string (2-3 authentic sentences, includes a specific job detail)",
      "author": "string (first name + last initial, e.g. Marcus T.)",
      "location": "string (a real city or area in North Texas)",
      "rating": 5
    }},
    {{
      "quote": "string",
      "author": "string",
      "location": "string",
      "rating": 5
    }},
    {{
      "quote": "string",
      "author": "string",
      "location": "string",
      "rating": 5
    }}
  ],
  "contact": {{
    "headline": "string (CTA headline, max 8 words)",
    "subtext": "string (1 reassuring sentence, max 20 words)",
    "form_disclaimer": "string (tiny text below form submit button, max 12 words)"
  }},
  "footer": {{
    "tagline": "string (short memorable motto, max 8 words)"
  }}
}}

Generate exactly {num_services} service objects in the same order as listed."""


# ── CLAUDE API ─────────────────────────────────────────────────────────────────

def call_claude(prompt: str, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0].strip()

    if not raw.startswith("{"):
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON found in Claude response:\n{raw[:400]}")
        raw = match.group(0)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned invalid JSON: {e}\n\nRaw:\n{raw[:400]}")


# ── RENDER HELPERS ─────────────────────────────────────────────────────────────

def _render_services(services: list) -> str:
    cards = []
    for s in services:
        name = html.escape(str(s.get("name", "")))
        icon = html.escape(str(s.get("icon", "🔧")))
        desc = html.escape(str(s.get("description", "")))
        highlight = html.escape(str(s.get("highlight", "")))
        cards.append(
            f'<div class="service-card">\n'
            f'  <div class="service-icon">{icon}</div>\n'
            f'  <h3>{name}</h3>\n'
            f'  <p>{desc}</p>\n'
            f'  <span class="service-highlight">{highlight}</span>\n'
            f'</div>'
        )
    return "\n".join(cards)


def _render_service_options(services: list) -> str:
    options = ['<option value="">&#8212; Select a service &#8212;</option>']
    for s in services:
        name = html.escape(str(s.get("name", "")))
        options.append(f'<option value="{name}">{name}</option>')
    return "\n".join(options)


def _render_testimonials(testimonials: list) -> str:
    cards = []
    for t in testimonials:
        quote = html.escape(str(t.get("quote", "")))
        author = html.escape(str(t.get("author", "")))
        location = html.escape(str(t.get("location", "")))
        rating = max(0, min(5, int(t.get("rating", 5))))
        stars = "★" * rating + "☆" * (5 - rating)
        cards.append(
            f'<div class="testimonial-card">\n'
            f'  <div class="stars">{stars}</div>\n'
            f'  <blockquote>{quote}</blockquote>\n'
            f'  <div class="testimonial-author">\n'
            f'    <strong>{author}</strong>\n'
            f'    <span>{location}, TX</span>\n'
            f'  </div>\n'
            f'</div>'
        )
    return "\n".join(cards)


# ── HTML RENDERER ──────────────────────────────────────────────────────────────

def render_html(config: dict, content: dict) -> str:
    c = config["contact"]
    t = config["theme"]

    replacements = {
        "{{PAGE_TITLE}}":           html.escape(config["meta"]["page_title"]),
        "{{META_DESC}}":            html.escape(config["meta"]["meta_description"]),
        "{{PRIMARY_COLOR}}":        t.get("primary_color", "#1B3A5C"),
        "{{ACCENT_COLOR}}":         t.get("accent_color", "#D4A843"),
        "{{DARK_COLOR}}":           t.get("dark_color", "#111827"),
        "{{LIGHT_BG}}":             t.get("light_bg", "#F8F9FA"),
        "{{PHONE}}":                html.escape(c.get("phone", "")),
        "{{EMAIL}}":                html.escape(c.get("email", "")),
        "{{SERVICE_AREA}}":         html.escape(c.get("service_area", "")),
        "{{HOURS_WEEKDAY}}":        html.escape(config["hours"].get("weekdays", "")),
        "{{HOURS_SAT}}":            html.escape(config["hours"].get("saturday", "")),
        "{{HOURS_SUN}}":            html.escape(config["hours"].get("sunday", "")),
        "{{HERO_HEADLINE}}":        html.escape(content["hero"]["headline"]),
        "{{HERO_SUBTITLE}}":        html.escape(content["hero"]["subtitle"]),
        "{{CTA_TEXT}}":             html.escape(content["hero"]["cta_text"]),
        "{{CTA_SUBTEXT}}":          html.escape(content["hero"]["cta_subtext"]),
        "{{SERVICES_HTML}}":        _render_services(content["services"]),
        "{{SERVICE_OPTIONS_HTML}}": _render_service_options(content["services"]),
        "{{TESTIMONIALS_HTML}}":    _render_testimonials(content["testimonials"]),
        "{{CONTACT_HEADLINE}}":     html.escape(content["contact"]["headline"]),
        "{{CONTACT_SUBTEXT}}":      html.escape(content["contact"]["subtext"]),
        "{{FORM_DISCLAIMER}}":      html.escape(content["contact"]["form_disclaimer"]),
        "{{FOOTER_TAGLINE}}":       html.escape(content["footer"]["tagline"]),
    }

    result = HTML_TEMPLATE
    for token, value in replacements.items():
        result = result.replace(token, value)
    return result


# ── OUTPUT ─────────────────────────────────────────────────────────────────────

def write_output(html_content: str, path: str) -> None:
    out_dir = os.path.dirname(os.path.abspath(path))
    os.makedirs(out_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_content)


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "business_config.json"
    output_path = "output/index.html"

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit(
            "Error: ANTHROPIC_API_KEY environment variable is not set.\n"
            "  export ANTHROPIC_API_KEY=sk-ant-..."
        )

    print(f"Loading config: {config_path}")
    config = load_config(config_path)

    print("Building prompt...")
    prompt = build_claude_prompt(config)

    print("Calling Claude API to generate website copy...")
    content = call_claude(prompt, api_key)

    print("Rendering HTML...")
    html_output = render_html(config, content)

    print(f"Writing: {output_path}")
    write_output(html_output, output_path)

    abs_path = os.path.abspath(output_path)
    print(f"\nDone! Open your website:")
    print(f"  file://{abs_path}")


if __name__ == "__main__":
    main()
