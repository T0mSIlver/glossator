"""Pin the text of every prompt constant in the evaluation package.

Prompt text is hashed into every generated question, record and verdict (D-023), so a
refactor that moves a constant between modules must not change a byte of it. Constants
are keyed by name rather than module so they can move freely; a re-export of the same
constant collapses into one entry. The judge templates are named `*_SYSTEM`, `*_USER` and
`*_CITATION` rather than `*_PROMPT`, hence the wider net.
"""

import hashlib
import importlib
import pkgutil

import glossator.eval

NAME_PARTS = ("PROMPT", "INSTRUCTIONS", "SYSTEM", "USER", "CITATION", "PRODUCT")

PINNED: dict[str, list[str]] = {
    "API_REFERENCE_INSTRUCTIONS": [
        "fdfea635b8236dcbcc2c96235d099ef74b8ccd9ce12ac3e60c16e3c9f3fa9b90",
    ],
    "CAPABILITY_INSTRUCTIONS": [
        "e4432b33012475c8496c9187dc375fcf6b9626ccbb323af63444a802db5702da",
    ],
    "CLOSED_BOOK_INSTRUCTIONS": [
        "c6763315257df0c22b7372deacc4bd59f9590582bf365a98b0875a240929498e",
    ],
    "CORPUS_CHECK_INSTRUCTIONS": [
        "4f76bb70e8f598174e0e20e336fdc90015b0e2ebd8c5a00cdc9a0109d93b4caf",
    ],
    "CROSS_PAGE_INSTRUCTIONS": [
        "085e21dfc9262fbbd8d51bb2a6b4acf264323de53d0504e955234b5703f98f67",
    ],
    "DEFECT_SYSTEM": [
        "2dff9e4c2ae22e87b3703aab6a937bd5038429638c5ff5bfb675879cdcc4ce81",
    ],
    "DEFECT_USER": [
        "77564d9ba6798f8ba997d5f95173da9e73ce58aa6d0d4ee314f19ccc9db0a7fe",
    ],
    "DEFECT_VERSION": [
        "1f98a0c389934b4ce9aff07056371a8d25ad989cb89894ea3c0bfbd482e3bed5",
    ],
    "FILTER_INSTRUCTIONS": [
        "a9e6c5ec790ccdf7501c17c3bd279f32430483d6d070c15735762939a914ed59",
        "cf348c523ad8613785ef3c104d685c01057bed02c1c6f8db16258a0f193fc5e8",
    ],
    "JUDGE_CITATION": [
        "d1565f592953cb6805137ed8fc6c4174a6d46d11161471a061dca79189e1736a",
    ],
    "JUDGE_NO_CITATIONS": [
        "152a5f298677af9b0aefd4f3117f78a35b073a2bf6777e259b526edda4ad8c5a",
    ],
    "JUDGE_SYSTEM": [
        "3b300bf0bcd8ea7f34e6afcb25a57aa810d5d01fc31e90e831053dee33229ae9",
        "eb1a8e3075de3636048122baf01e67ba54cc8f76ffdf53e73f468d5afe2eb832",
    ],
    "JUDGE_USER": [
        "4e976b80283c725709131760638253f997f55e11f668470237a8187c4269aa7f",
    ],
    "JUDGE_VERSION": [
        "0a80e3d17dbffc5646a472f7dc6fffcf91b9c7caa723a6f02ba51740c1f48493",
    ],
    "PAGE_ALONE_INSTRUCTIONS": [
        "86604a8deb155fe0d53d818fc18e9ff7679013375a087476b1ebb502713a7f1e",
    ],
    "POST_CUTOFF_INSTRUCTIONS": [
        "ca45c4fe112ffadc4e7f00a16f1247d62622f36795369e27005b44b0f5ae9e28",
    ],
    "PRODUCT": [
        "d25e414b7a3833a2d1b884b858aad5929f55bd2a014e868810133fa51ca7f1f1",
    ],
    "PROMPT_LEAD": [
        "dc0639b47a29055552cd7a0e58e4cbc85e76c06eb77d6d773727f0ff4c94d106",
    ],
    "PROMPT_VERSION": [
        "3bfc269594ef649228e9a74bab00f042efc91d5acc6fbee31a382e80d42388fe",
        "3d0cc940ffc4a6fedee6afe294b6b547cd491d4dbfc845ee8cb8a49449b5e20b",
        "ceb5071ae957642915c70d747e565daaa911d95ff33137643182661ee9f07c96",
    ],
    "RERANK_PROMPT_VERSION": [
        "3f1c9f35b211854a1df6d88a0a86386a0adea08457a8d3f469e3369c0f501e37",
    ],
    "SINGLE_SECTION_INSTRUCTIONS": [
        "4970bc4e4762400776a0a94005e312946ad382e07e23024894af4171fe0f6a22",
    ],
    "SYSTEM": [
        "50e3deb86032f019a4e8ba0de4d5cb44a1703f80bf6ef78e61663aaf49849af5",
        "a7b363cb1e843846d5300636828b74178171905b18942b7dc9aad2e91a8b997a",
    ],
    "SYSTEM_PROMPT": [
        "257020c170449aad411ccbb15850c62248f09407c8a2106c89ac6c032b0c8270",
    ],
    "UNANSWERABLE_INSTRUCTIONS": [
        "f7b884df810c1f1b6c10a61e1de84935840c20359d71567138fa47c275ff7644",
    ],
}


def is_prompt_constant(name: str) -> bool:
    return name.isupper() and (any(part in name for part in NAME_PARTS) or name.endswith("VERSION"))


def prompt_hashes() -> dict[str, list[str]]:
    found: dict[str, set[str]] = {}
    for info in pkgutil.walk_packages(glossator.eval.__path__, "glossator.eval."):
        # Importing a `__main__` module would run its command line.
        if info.name.endswith(".__main__"):
            continue
        module = importlib.import_module(info.name)
        for name, value in vars(module).items():
            if isinstance(value, str) and is_prompt_constant(name):
                digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
                found.setdefault(name, set()).add(digest)
    return {name: sorted(digests) for name, digests in sorted(found.items())}


def test_prompt_constants_are_unchanged() -> None:
    assert prompt_hashes() == PINNED


if __name__ == "__main__":
    import json

    print(json.dumps(prompt_hashes(), indent=4))
