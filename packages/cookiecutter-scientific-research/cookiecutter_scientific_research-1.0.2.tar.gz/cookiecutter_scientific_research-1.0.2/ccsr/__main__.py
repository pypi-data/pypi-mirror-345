# Monkey-patch jinja to allow variables to not exist, which happens with sub-options
import jinja2

jinja2.StrictUndefined = jinja2.Undefined


# Monkey-patch cookiecutter to allow sub-items
from cookiecutter import prompt

from ccsr.monkey_patch import prompt_for_config

prompt.prompt_for_config = prompt_for_config


# monkey-patch context to point to ccsr.json
from cookiecutter import generate

from ccsr.monkey_patch import generate_context_wrapper

generate.generate_context = generate_context_wrapper

# for use in tests need monkey-patched api main
from cookiecutter import cli
from cookiecutter import main as api_main  # noqa: F401 referenced by tests

from ccsr import __version__


def default_ccsr_main(f):
    """Set the default for the cookiecutter template argument to the ccsr template."""

    def _main(*args, **kwargs):
        f.params[1].default = (
            "https://github.com/waynexucn/cookiecutter-scientific-research"
        )
        # Find the "checkout" option in the cookiecutter cli (currently the fifth)
        # Per #389, set this to the currently released version by default
        param_names = [p.name for p in f.params]
        checkout_index = param_names.index("checkout")
        f.params[checkout_index].default = f"v{__version__}"
        return f(*args, **kwargs)

    return _main


main = default_ccsr_main(cli.main)


if __name__ == "__main__":
    main()
