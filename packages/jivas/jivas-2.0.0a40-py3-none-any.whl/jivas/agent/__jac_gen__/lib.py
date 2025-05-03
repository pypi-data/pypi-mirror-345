from __future__ import annotations
from jaclang import *
import typing
from enum import Enum, auto
if typing.TYPE_CHECKING:
    from jivas.agent.core import init_agents, import_agent, export_descriptor, export_daf, get_agent, update_agent, list_agents, delete_agent, healthcheck
else:
    init_agents, import_agent, export_descriptor, export_daf, get_agent, update_agent, list_agents, delete_agent, healthcheck = jac_import('jivas.agent.core', items={'init_agents': None, 'import_agent': None, 'export_descriptor': None, 'export_daf': None, 'get_agent': None, 'update_agent': None, 'list_agents': None, 'delete_agent': None, 'healthcheck': None})
if typing.TYPE_CHECKING:
    from jivas.agent.action import interact, pulse, list_actions, get_action, update_action, install_action, uninstall_action
else:
    interact, pulse, list_actions, get_action, update_action, install_action, uninstall_action = jac_import('jivas.agent.action', items={'interact': None, 'pulse': None, 'list_actions': None, 'get_action': None, 'update_action': None, 'install_action': None, 'uninstall_action': None})
if typing.TYPE_CHECKING:
    from jivas.agent.memory import get_frames, get_interactions
else:
    get_frames, get_interactions = jac_import('jivas.agent.memory', items={'get_frames': None, 'get_interactions': None})
if typing.TYPE_CHECKING:
    from jivas.agent.analytics import get_channels_by_date, get_users_by_date, get_interactions_by_date, get_interaction_logs
else:
    get_channels_by_date, get_users_by_date, get_interactions_by_date, get_interaction_logs = jac_import('jivas.agent.analytics', items={'get_channels_by_date': None, 'get_users_by_date': None, 'get_interactions_by_date': None, 'get_interaction_logs': None})