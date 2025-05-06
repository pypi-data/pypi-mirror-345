from clight.system.importer import *


class SemVer:
    ####################################################################################// Load
    def __init__(self, default_tag: str = 'alpha'):
        self.test = False
        self.default_tag = default_tag

    ####################################################################################// Main
    def bump(current: str = "0.0.0", action: str = None):
        obj = SemVer()
        obj.test = action != None

        if not SemVer.valid(current):
            cli.error(f"Invalid current version: " + current)
            return ""

        parts = obj.__getParts(current)
        if not obj.test:
            if parts.tag:
                promote = obj.__askPromotion(parts.major, parts.minor, parts.patch, parts.tag)
                if promote:
                    return promote
            action = obj.__askChangeType()
        
        if action not in ["major", "minor", "patch"]:
            return ""

        if not obj.test and action == "major" and not parts.tag:
            stage = obj.__askStage()
            if stage:
                number = obj.__bumpNumber(action, parts.major, parts.minor, parts.patch)
                return number + stage

        if parts.tag:
            return obj.__bumpTag(action, parts.major, parts.minor, parts.patch, parts.tag, parts.tagN)

        return obj.__bumpNumber(action, parts.major, parts.minor, parts.patch)

    def valid(version: str):
        semver_regex = re.compile(
            r"""
            ^                        # start of string
            (0|[1-9]\d*)             # major
            \.
            (0|[1-9]\d*)             # minor
            \.
            (0|[1-9]\d*)             # patch
            (?:-                     # optional suffix
              (?:
                (?:                  # — pre-release branch —
                  (?:alpha|beta|rc)  #   must be one of these
                  (?:\.(?:0|[1-9]\d*))*  #   optional .number segments (no leading zeros)
                )
              |
                (?:                  # — build‐metadata branch —
                  build              #   literal “build”
                  (?:\.[\da-zA-Z-]+)*   #   dot‐separated alphanumeric (leading zeros OK)
                )
              )
            )?                       # suffix is entirely optional
            $                        # end of string
            """,
            re.VERBOSE,
        )

        return bool(semver_regex.match(version))

    ####################################################################################// Tests
    def test_check():
        return SemVer.__test_check({
            "1.0.0": True,
            "2.5.1-alpha": True,
            "0.9.0-alpha.1": True,
            "0.9.0-alpha.": False,
            "0.9.0-.": False,
            "0.9.0-rc.": False,
            "0.9.0-rc.1": True,
            "0.9.0-beta.123": True,
            "102.900.223-alpha.123": True,
            "102.900.223-beta.123": True,
            "102.900.223-tota": False,
            "102.900.223-": False,
            "1.0.0-0.3.7": False,
            "1.0.0-0.3.": False,
            "1.2.3+build.001": False,
            "1.2.3-build.001": True,
            "102.900.023-alpha.123": False,
            "01.2.3": False,  
            "1.02.3": False,  
            "1.2.03": False,  
            "1.2": False,
            "1.2.": False,
            "...": False,
            "1...": False,
            "1.2.3-": False,
        })

    def test_bump():
        return SemVer.__test_bump([
            # Stable bumps
            ("1.2.1", "patch", "1.2.2"),
            ("1.2.1", "minor", "1.3.0"),
            ("1.2.1", "major", "2.0.0"),
            # More stable cases
            ("10.4.6", "patch", "10.4.7"),
            ("10.4.6", "minor", "10.5.0"),
            ("10.4.6", "major", "11.0.0"),
            # Alpha prerelease bumps
            ("6.1.0-alpha.1", "patch", "6.1.0-alpha.2"),
            ("6.1.0-alpha.1", "minor", "6.2.0-alpha.1"),
            ("6.1.0-alpha.1", "major", "7.0.0-alpha.1"),
            ("1.0.0-alpha.9", "patch", "1.0.0-alpha.10"),
            ("1.0.0-alpha.9", "minor", "1.1.0-alpha.1"),
            # Beta prerelease bumps
            ("6.1.0-beta.1", "patch", "6.1.0-beta.2"),
            ("6.1.0-beta.1", "minor", "6.2.0-alpha.1"),
            ("6.1.0-beta.1", "major", "7.0.0-alpha.1"),
            ("2.0.0-beta.9", "patch", "2.0.0-beta.10"),
            ("2.0.0-beta.9", "minor", "2.1.0-alpha.1"),
            ("2.0.0-beta.9", "major", "3.0.0-alpha.1"),
            # RC prerelease bumps
            ("6.1.0-rc.1", "patch", "6.1.0-rc.2"),
            ("6.1.0-rc.1", "minor", "6.2.0-alpha.1"),
            ("6.1.0-rc.1", "major", "7.0.0-alpha.1"),
            ("1.0.0-rc.9", "patch", "1.0.0-rc.10"),
            ("1.0.0-rc.9", "minor", "1.1.0-alpha.1"),
            ("1.0.0-rc.9", "major", "2.0.0-alpha.1"),
            # Edge cases: zero versions
            ("0.0.0", "patch", "0.0.1"),
            ("0.0.0", "minor", "0.1.0"),
            ("0.0.0", "major", "1.0.0"),
            # Error handling tests
            ("1.2.3", "inval", "Invalid bump type 'inval'. Use 'patch', 'minor', or 'major'."),
            ("1.2", "patch", "Invalid version string: '1.2'"),
            ("1.2.3.4", "patch", "Invalid version string: '1.2.3.4'"),
        ])

    ####################################################################################// Helpers
    def __getParts(self, current: str):
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z]+)\.(\d+))?$'
        match = re.match(pattern, current)

        parts = types.SimpleNamespace()
        parts.major, parts.minor, parts.patch = map(int, match.groups()[:3])
        parts.tag = match.group(4)
        parts.tagN = int(match.group(5)) if match.group(5) else None

        return parts

    def __askPromotion(self, major: int, minor: int, patch: int, tag: int):
        new = self.__askStagePromotion(tag)
        if new != tag:
            if not new:
                return f"{major}.{minor}.{patch}"
            return f"{major}.{minor}.{patch}-{new}.1"
        return ""

    def __bumpTag(self, action: str, major: int, minor: int, patch: int, tag: int, tagN: int):
        if action == "patch":
            new_pr_num = tagN + 1
            return f"{major}.{minor}.{patch}-{tag}.{new_pr_num}"

        if action == "minor":
            minor += 1
            patch = 0
        else:  # major
            major += 1
            minor = 0
            patch = 0

        return f"{major}.{minor}.{patch}-{self.default_tag}.1"

    def __bumpNumber(self, action: str, major: int, minor: int, patch: int):
        if action == "patch":
            patch += 1
        elif action == "minor":
            minor += 1
            patch = 0
        else:  # major bump
            major += 1
            minor = 0
            patch = 0

        return f"{major}.{minor}.{patch}"

    def __askStagePromotion(self, tag: str):
        if self.test:
            return tag
        elif tag == "alpha" and cli.confirmation('Is it ready to be promoted to "beta" stage?'):
            return "beta"
        elif tag == "beta" and cli.confirmation('Is it ready to be promoted to "rc" stage as release candidate?'):
            return "rc"
        elif tag == "rc" and cli.confirmation('Is it ready to be released as "stable" version?'):
            return ""
        else:
            return tag

    def __askStage(self):
        options = {
            "Stable - Good to go live!": "",
            "Alpha - Still building things out": "-alpha.1",
            "Beta - All there, but testing needed": "-beta.1",
            "RC - Just about done, final checks": "-rc.1",
        }

        selected = cli.selection("What stage are you moving to?", list(options.keys()), True)

        return options[selected]

    def __askChangeType(self):
        options = {
            "Patch - Everything works the same, but bugs were fixed or small internal improvements made": "patch",
            "Minor - Everything still works, plus they get new features or enhancements": "minor",
            "Major - Their existing code might break, or behavior has changed in an incompatible way": "major",
        }

        selected = cli.selection("What will your users or clients experience with this change?", list(options.keys()), True)

        return options[selected]

    def __test_check(cases: dict ={}):
        cli.info(f"Must  | Got   | Case")
        cli.info("--------------------------------------------")
        for case in cases:
            expect = cases[case]
            result = SemVer.valid(case)
            if cases[case] == result:
                cli.done(f"{str(expect):5s} | {str(result):6s}| {case}")
                continue
            print(f"{str(expect):5s} | {str(result):6s}| {case}")
        cli.info("--------------------------------------------\n")
        sys.exit()

    def __test_bump(cases: list =[]):
        cli.info(f"Case  | Current       | New")
        cli.info("--------------------------------------------")
        for version, action, expected in cases:
            result = SemVer.bump(version, action)
            if result == expected:
                cli.done(f"{action:6s}| {str(version):13s} | {str(result):6s}")
            else:
                print(f"{action:6s}| {str(version):13s} | {str(result):6s}")
        cli.info("--------------------------------------------\n")
        sys.exit()
