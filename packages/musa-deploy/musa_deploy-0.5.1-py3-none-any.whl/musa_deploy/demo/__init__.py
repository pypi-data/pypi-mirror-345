from .demo import (
    TorchMusaDeployer,
    vLLMDeployer,
    vLLMMusaDeployer,
    KuaeDeployer,
    OllamaDeployer,
)

from musa_deploy.check.utils import CheckModuleNames

DEMO = dict()
DEMO[CheckModuleNames.torch_musa.name] = TorchMusaDeployer()
DEMO[CheckModuleNames.vllm.name] = vLLMDeployer()
DEMO["vllm_musa"] = vLLMMusaDeployer()
DEMO["kuae"] = KuaeDeployer()
DEMO["ollama"] = OllamaDeployer()
