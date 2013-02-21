import mg.constructor
from mg.constructor.design import DesignGenerator
from mg.core.tools import *
import re
import random

re_design_url = re.compile('^[a-z0-9_]+/(.+)$', re.IGNORECASE)

class DesignCombatCommonBlocks(DesignGenerator):
    def group(self):
        return "combatinterface"

    def generate_files(self):
        vars = {
            "tpl": self.id(),
            "lang": self.call("l10n.lang"),
        }
        data = self.call("web.parse_template", "combatinterface/common-blocks.html", vars)
        self.add_file("global.html", "text/html", data)
        vars = {
            "tpl": self.id(),
            "lang": self.call("l10n.lang"),
        }
        self.add_file("main.css", "text/css", self.call("web.parse_template", "combatinterface/common-blocks.css", vars))

class DesignCombatRustedMetal(DesignCombatCommonBlocks):
    def id(self): return "combat-rusted-metal"
    def name(self): return self._("Rusted Metal")
    def preview(self): return "/st/constructor/design/gen/combat-rusted-metal.jpg"

def design_class_wrapper(cls, tp):
    class DesignClass(cls):
        def group(self):
            return "combatinterface-%s" % tp
    return DesignClass

class CombatInterface(mg.constructor.ConstructorModule):
    def register(self):
        self.rhook("combat.vars-log", self.combat_vars_log)
        self.rhook("combat.parse", self.parse, priority=10)
        self.rhook("combat.response", self.response, priority=10)
        self.rhook("combat.response_template", self.response_template, priority=10)
        self.rhook("combat.response_simple", self.response_simple, priority=10)
        self.rhook("combat.response_simple_template", self.response_simple_template, priority=10)

    def combat_vars_log(self, vars):
        vars["title"] = self._("Combat log")
        vars["to_page"] = self._("Pages")

    def parse(self, template, vars):
        self.call("combat.setup-interface", vars)
        design = self.design("combatinterface")
        return self.call("design.parse", design, template, None, vars, "combat")

    def response(self, content, vars):
        self.call("combat.setup-interface", vars)
        design = self.design("combatinterface")
        self.call("design.response", design, "global.html", content, vars, "combat")

    def response_template(self, template, vars):
        self.call("combat.setup-interface", vars)
        design = self.design("combatinterface")
        content = self.call("design.parse", design, template, None, vars, "combat")
        self.call("design.response", design, "global.html", content, vars, "combat")

    def response_simple(self, content, vars):
        self.call("combat.setup-interface", vars)
        design = self.design("combatinterface")
        self.call("design.response", design, "global-simple.html", content, vars, "combat")

    def response_simple_template(self, template, vars):
        self.call("combat.setup-interface", vars)
        design = self.design("combatinterface")
        content = self.call("design.parse", design, template, None, vars, "combat")
        self.call("design.response", design, "global-simple.html", content, vars, "combat")

class CombatInterfaceAdmin(mg.constructor.ConstructorModule):
    def register(self):
        self.rhook("admin-designs.subdirs", self.subdirs)
        for tp in self.conf("combats.rules", {}).keys():
            self.rhook("ext-admin-combatinterface-%s.design" % tp, curry(self.ext_design, tp), priv="design")
            self.rhook("headmenu-admin-combatinterface-%s.design" % tp, curry(self.headmenu_design, tp))
            self.rhook("admin-combatinterface-%s.validate" % tp, self.validate)
            self.rhook("admin-combatinterface-%s.previews" % tp, self.previews)
            self.rhook("admin-combatinterface-%s.preview" % tp, self.preview)
            self.rhook("admin-combatinterface-%s.generators" % tp, curry(self.generators, tp))
            self.rhook("admin-combatinterface-%s.design-files" % tp, self.design_files)

    def subdirs(self, subdirs):
        for tp in self.conf("combats.rules", {}).keys():
            subdirs["combatinterface-%s" % tp] = "combat"

    def generators(self, tp, gens):
        gens.append(design_class_wrapper(DesignCombatRustedMetal, tp))
        #gens.append(DesignCombatCelticCastle)
        #gens.append(DesignCombatJungle)
        #gens.append(DesignCombatMedieval)
        #gens.append(DesignCombatPinky)
        #gens.append(DesignCombatSpace)
        #gens.append(DesignCombatSubmarine)

    def headmenu_design(self, tp, args):
        if args == "":
            rules = self.conf("combats.rules", {}).get(tp)
            if rules is not None:
                return [self._("combats///%s: design") % htmlescape(rules.get("name")), "combats/rules"]
        else:
            return self.call("design-admin.headmenu", "combatinterface-%s" % tp, args)

    def ext_design(self, tp):
        rules = self.conf("combats.rules", {}).get(tp)
        if rules is None:
            self.call("admin.redirect", "combats/rules")
        self.call("admin.advice", {"title": self._("Documentation"), "content": self._('Read <a href="//www.%s/doc/design/combatinterface" target="_blank">the combat interface design reference manual</a> to create your own template or edit generated one') % self.main_host, "order": 30})
        self.call("design-admin.editor", "combatinterface-%s" % tp)

    def validate(self, design, parsed_html, errors):
        files = design.get("files")
        if not design.get("css"):
            errors.append(self._("Combat interface design package must contain a CSS file"))

    def previews(self, design, previews):
        previews.append({"filename": "log.html", "title": self._("Combat log")})

    def preview(self, design, filename):
        vars = {}
        if filename == "log.html":
            vars["title"] = self._("Combat log")
            vars["combat_title"] = random.choice([
                self._("The Monster attacks John"),
                self._("Epic battle near the main gates of the Rockbridge Castle"),
                self._("Extremely long combat name involving names of participating characters, NPCs and so on"),
            ])
            vars["counters"] = ""
            for i in range(0, random.randrange(0, 5)):
                vars["counters"] += ' <img src="/st/constructor/design/counter%d.gif" alt="" />' % random.randrange(0, 4)
            if random.random() < 0.5:
                pages = []
                for i in range(0, random.randrange(2, random.choice([3, 5, 10, 20, 50]))):
                    pages.append({"entry": {"text": i + 1, "a": {"href": "#"}}})
                pages[-1]["lst"] = True
                vars["pages"] = pages
            entries = []
            members = [
                self._("God"),
                self._("Devil"),
                self._("Angel"),
                self._("Daemon"),
                self._("Spirit"),
                self._("Ghost"),
            ]
            attacks = [
                self._("combat///attacked"),
                self._("combat///kicked"),
                self._("combat///pushed"),
                self._("combat///jumped on"),
                self._("combat///killed"),
                self._("combat///frozen"),
            ]
            show_time = random.random() < 0.8
            time = 0
            for i in range(0, random.choice([10, 50, 100, 200])):
                participants = random.sample(members, 2)
                source = participants[0]
                target = participants[1]
                attack = random.choice(attacks)
                max_hp = random.randrange(50, 10000)
                damage = random.randrange(30, max_hp - 20)
                hp = random.randrange(0, max_hp - damage)
                if random.random() < 0.2:
                    cls = "combat-log-important"
                else:
                    cls = None
                text = u'<span class="combat-log-member">%s</span> <span class="combat-log-attack">%s</span> <span class="combat-log-member">%s</span> <span class="combat-log-damage">-%d</span> <span class="combat-log-hp">[%d/%d]</span>' % (source, attack, target, damage, hp, max_hp)
                if show_time:
                    time += random.choice([1, 3, 5, 10, 20])
                    text = u'<span class="combat-log-time">%d:%02d</span> %s' % (time / 60, time % 60, text)
                entries.append({
                    "cls": cls,
                    "text": text
                })
            entries[-1]["lst"] = True
            vars["entries"] = entries
            self.call("combat.vars-log", vars)
        else:
            self.call("web.not_found")
        content = self.call("design.parse", design, filename, None, vars, "combat")
        self.call("design.response", design, "global.html", content, vars, design_type="combat")

    def design_files(self, files):
        files.append({"filename": "log.html", "description": self._("Combat log"), "doc": "/doc/design/combatinterface"})

