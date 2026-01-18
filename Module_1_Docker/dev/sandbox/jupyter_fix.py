#if crash freeze for interactive python
'''
Command: uv pip install ipykernel -U --force-reinstall
import os
os._exit(00)

from ipylab import JupyterFrontEnd
app = JupyterFrontEnd()
app.commands.execute('kernelmenu:restart')
'''