import ast
import json
from typing import Any, Literal
from components.data.models import postgres as PostgresModels
from components.data.schemas import scenario as ScenarioSchemas
from components.repositories.business import BusinessRepository
from components.repositories.scenario import ScenarioRepository


class Node:
    def __init__(self, node_id: int, action_id: int, name):
        self.id = node_id
        self.name = name
        self.aid = action_id

    @staticmethod
    def from_dict(node_id: int, dict_data: dict[str, Any]):
        return Node(node_id, dict_data["aid"], dict_data["name"])

    def to_dict(self):
        # id is get directly from the object, no need to put it in the dictionary
        return {"name": self.name, "aid": self.aid}


class Action:
    def __init__(self, action_id: int, name, action_type, data):
        self.id = action_id
        self.name = name
        self.type = action_type
        self.data = data

    @staticmethod
    def from_dict(action_id: int, data: dict[str, Any]):
        return Action(action_id, data["name"], data["type"], data["data"])

    def to_dict(self):
        # id is get directly from the object, no need to put it in the dictionary
        return {"name": self.name, "type": self.type, "data": self.data}


class Route:
    def __init__(self, node_id_start: int, node_id_end: int, rule):
        self.nid_start = node_id_start
        self.nid_end = node_id_end
        self.rule = rule

    def to_dict(self):
        return {"nid_start": self.nid_start, "nid_end": self.nid_end, "rule": self.rule}

    @staticmethod
    def from_dict(node_id_start: int, node_id_end: int, data: dict[str, Any]):
        return Route(node_id_start, node_id_end, data["rule"])


class Flow:
    def __init__(self):
        self.nodes: dict[int, Node] = {}  # Dictionary of node IDs to Node objects
        self.actions: dict[int, Action] = {}  # Dictionary of action IDs to Action objects
        self.routes: dict[int, dict[int, Route]] = {}  # Dictionary of route IDs to Route objects
        self.next_node_id = 1
        self.next_action_id = 1

    def add_action(self, action_name, action_type, action_data):
        action = Action(self.next_action_id, action_name, action_type, action_data)
        self.actions[action.id] = action
        self.next_action_id += 1
        return action

    def edit_action(self, action_id: int, new_name, new_type, new_data):
        action = self.actions.get(action_id)
        assert action is not None, "Action not found"
        action.name = new_name
        action.type = new_type
        action.data = new_data

    def delete_action(self, action_id: int):
        # check if the action is used in any node
        for node in self.nodes.values():
            if node.aid == action_id:
                raise Exception("Action is used in a node")
        self.actions.pop(action_id, None)

    def add_node(self, node_name, action_id: int):
        node = Node(self.next_node_id, action_id, node_name)
        self.nodes[node.id] = node
        self.next_node_id += 1
        return node

    def edit_node(self, node_id: int, new_name, new_action_id: int):
        node = self.nodes.get(node_id)
        assert node is not None, "Node not found"
        assert new_action_id in self.actions, "Invalid action ID"
        node.name = new_name
        node.aid = new_action_id

    def add_route(self, node_id_start: int, node_id_end: int, rule):
        assert node_id_start in self.nodes and node_id_end in self.nodes, "Invalid node ID"
        route = Route(node_id_start, node_id_end, rule)
        if node_id_start not in self.routes:
            self.routes[node_id_start] = {}
        self.routes[node_id_start][node_id_end] = route
        return route

    def edit_route(self, node_id_start: int, node_id_end: int, new_rule):
        assert node_id_start in self.nodes and node_id_end in self.nodes, "Invalid node ID"
        route = self.routes[node_id_start].get(node_id_end)
        assert route is not None, "Route not found"
        route.rule = new_rule

    def delete_route(self, node_id_start: int, node_id_end: int):
        self.routes[node_id_start].pop(node_id_end, None)
        if len(self.routes[node_id_start]) == 0:
            self.routes.pop(node_id_start, None)

    def delete_node(self, node_id: int):
        node = self.nodes.get(node_id)
        assert node is not None, "Node not found"
        self.nodes.pop(node_id, None)
        self.routes.pop(node_id, None)
        for node_id_end_routes in self.routes.values():
            node_id_end_routes.pop(node_id, None)  # all routes that goes to the deleted node

    def serialize(self, output_type: Literal["json", "python"] = "json"):
        data = {
            "nn": self.next_node_id,
            "na": self.next_action_id,
            "nodes": {node.id: node.to_dict() for node in self.nodes.values()},
            "actions": {action.id: action.to_dict() for action in self.actions.values()},
            "routes": {node_id_start: {node_id_end: route.to_dict()
                                       for node_id_end, route in node_id_end_routes.items()}
                       for node_id_start, node_id_end_routes in self.routes.items()}
        }
        # pprint(data, sort_dicts=False, indent=4)
        return json.dumps(data) if output_type == "json" else str(data)

    @staticmethod
    def deserialize(serialized_data: str, input_type: Literal["json", "python"] = "json") -> tuple[Any, Any]:
        try:
            data = json.loads(serialized_data) if input_type == "json" else ast.literal_eval(serialized_data)
            deserialized_flow = Flow()
            deserialized_flow.next_node_id = data["nn"]
            deserialized_flow.next_action_id = data["na"]

            for node_id_key, node_data in data["nodes"].items():
                node_id = int(node_id_key) if input_type == "json" else node_id_key
                deserialized_flow.nodes[node_id] = Node.from_dict(node_id, node_data)

            for action_id_key, action_data in data["actions"].items():
                action_id = int(action_id_key) if input_type == "json" else action_id_key
                deserialized_flow.actions[action_id] = Action.from_dict(action_id, action_data)

            for node_id_start, node_id_end_routes in data["routes"].items():
                node_id_start = int(node_id_start) if input_type == "json" else node_id_start
                deserialized_flow.routes[node_id_start] = {}
                for node_id_end, route_data in node_id_end_routes.items():
                    node_id_end = int(node_id_end) if input_type == "json" else node_id_end
                    deserialized_flow.routes[node_id_start][node_id_end] = Route.from_dict(node_id_start, node_id_end, route_data)

            return deserialized_flow, None
        except Exception as e:
            print(e)
            return None, "Invalid serialized data"

    def print_readable(self):
        print("Nodes:")
        for node in self.nodes.values():
            print(f"\tN{node.id}: {node.name} (Action ID: A{node.aid})")
        print("Actions:")
        for action in self.actions.values():
            print(f"\tA{action.id}: \n\t\tType: {action.type}\n\t\tData: {action.data}")
        print("Routes:")
        for node_id_end_routes in self.routes.values():
            for route in node_id_end_routes.values():
                print(f"\tFrom node {route.nid_start} to node {route.nid_end} (Rule: {route.rule})")


class ScenarioService:
    def __init__(self, session, account: PostgresModels.Account | None = None):
        self.session = session
        self.repository = ScenarioRepository(session=session)
        self.account = account
        self.loaded_flows = {}

    def get_user_scenarios(self):
        scenarios = self.repository.get_all_by_account(identifier=self.account.id)
        return scenarios

    def get_user_scenario(self, scenario_id: int):
        scenario = self.repository.get(identifier=scenario_id)
        if scenario is None or scenario.id_account != self.account.id:
            return None
        return scenario

    def create_scenario(self, scenario_data: ScenarioSchemas.ScenarioPOST) -> tuple[Any, Any]:
        new_flow = Flow()
        business_repository = BusinessRepository(session=self.session)
        business = business_repository.get(identifier=scenario_data.id_business)
        if business is None or business.id_account != self.account.id:
            return None, "Business not found"
        new_scenario = PostgresModels.Scenario(**scenario_data.model_dump(), id_account=self.account.id, flow=new_flow.serialize())
        self.repository.create(new_scenario)
        return new_scenario, None

    def update_scenario(self, scenario_id: int, scenario_data: ScenarioSchemas.ScenarioPUT) -> tuple[Any, Any]:
        business_repository = BusinessRepository(session=self.session)
        business = business_repository.get(identifier=scenario_data.id_business)
        if business is None or business.id_account != self.account.id:
            return None, "Business not found"
        scenario = self.get_user_scenario(scenario_id)
        if scenario is None:
            return None, "Scenario not found"
        updated_scenario = self.repository.update(scenario_id, scenario_data)
        if updated_scenario is None:
            return None, "Scenario not found"
        return updated_scenario, None

    def delete_scenario(self, scenario_id: int) -> Any:
        scenario = self.get_user_scenario(scenario_id)
        if scenario is None:
            return "Scenario not found"
        self.repository.delete(identifier=scenario_id)
        return None

    def load_scenario_flow(self, scenario_id: int) -> Any:
        scenario = self.repository.get(identifier=scenario_id)
        if scenario is None or scenario.id_account != self.account.id:
            return "Scenario not found"
        self.loaded_flows[scenario_id] = Flow.deserialize(scenario.flow)
        return None
