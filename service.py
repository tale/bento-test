import bentoml
import spear_dsp

# Runtime environment defined via BentoML's Python SDK rather than a
# bentofile.yaml. spear-dsp lives on our private JFrog PyPI index, so we point
# pip at it (with PyPI as the fallback for everything else). Credentials are
# injected at build time as a secret-backed env var rather than baked into the
# image. lock_python_packages=False matches how the horizon packages build,
# since the private index doesn't play nicely with the lock step.
image = (
    bentoml.images.Image(python_version="3.12", lock_python_packages=False)
    .python_packages(
        "--index-url https://pypi.org/simple",
        "--extra-index-url https://${JFROG_USERNAME}:${JFROG_ACCESS_TOKEN}@spearai.jfrog.io/artifactory/api/pypi/spear-ai-pypi/simple",
        "bentoml==1.4.39",
        "spear-dsp==2.1.0",
    )
)


@bentoml.service(
    image=image,
    envs=[
        {"name": "JFROG_USERNAME", "value": "unset"},
        {"name": "JFROG_ACCESS_TOKEN", "value": "unset"},
    ],
)
class HelloSpearDsp:
    @bentoml.api
    def hello(self, seconds: float = 1.5) -> dict[str, object]:
        duration = spear_dsp.Duration.from_seconds(seconds)
        return {
            "message": "hello from spear_dsp via private JFrog",
            "input_seconds": seconds,
            "duration_seconds": duration.seconds(),
            "duration_microseconds": duration.microseconds(),
            "valid": duration.valid(),
        }
