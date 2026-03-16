from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from . import use_case_normalizer as ucn
from database.db_connect import connect_db
from database.db_query import find_pc_recommendations
from openai import OpenAI

########################################################################
# actions.py contains custom actions that are used to perform application 
# specific functionality.  
########################################################################

# Check PC database for PC recommendations that align with the user's responses
class ActionCheckPCDatabase(Action):

    def name(self) -> Text:
        return "action_check_pc_database"

    # build db field filter based on user conversation responses
    def populate_db_filter(self, tracker):
        use_case = tracker.get_slot("user_use_case")
        budget = tracker.get_slot("user_budget")
        ram_gb = tracker.get_slot("user_preferred_ram")
        device_type = tracker.get_slot("user_device_type")
        graphics_type = tracker.get_slot("user_needs_discrete_gpu")

        filters = {
            "price": None,
            "machine_type": None,
            "ram_gb": None,
            "graphics_type":None
        }

        default_use_case_specs = ucn.get_use_case_specs(use_case)

        if ram_gb is None:
            ram_gb = default_use_case_specs["min_ram_gb"]

        if graphics_type is None or str(graphics_type).lower() == "undecided":
            graphics_type = default_use_case_specs["graphics_type"]
      
        filters["price"] = budget
        filters["machine_type"] = device_type
        filters["ram_gb"] = ram_gb
        filters["graphics_type"] = graphics_type

        return filters

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        index = tracker.get_slot("recommendation_index") or 0

        filters = self.populate_db_filter(tracker)

        # Connect to database and call find_pc_recommendations to retrieve PC recommendation data
        connection = connect_db()
        results = find_pc_recommendations(connection, filters, offset=index)
        connection.close()

        # If no results found load the relevant conversation slots to allow the conversation to branc accordingly
        if not results:
            return [
                SlotSet("recommendation_index", None),
                SlotSet("pc_found", False)
            ]

        # Map database results
        current_pc = results[0]
        # Set has_more flag to true if there are more results available
        has_more = len(results) > 1

        # Generate PC recommendation response message
        message = "Here is a recommendation:\n\n" + self.build_pc_table(current_pc)

        # Send message to user via chatbot
        dispatcher.utter_message(text=message)

        new_index = index + 1 if has_more else None

        # Set the RASA slot fields
        return [
            SlotSet("recommendation_index", new_index),
            SlotSet("pc_found", True),
            SlotSet("user_view_next_pc", None),
            SlotSet("pc_data", message)
        ]
    
    # Generate formatted PC Recommendation response based on pc data returned from database
    def build_pc_table(self,pc: dict) -> str:
        rows = []

        ignore_keys=["listing_id","model_id","processor_id","graphics_id"]

        for key, value in pc.items():
            if value is None or key.lower() in ignore_keys:
                continue  # skip empty fields or keys that should be ignored

            # Format field name
            field_name = key.replace("_", " ").title()

            # Special formatting
            if key == "price":
                value = f"£{value:.2f}"
            elif key == "processor_speed_ghz":
                value = f"{value} GHz"
            elif key == "ram_gb":
                value = f"{value} GB"
            elif key == "graphics_ram_gb":
                if value == 0:
                    continue
                else:
                     value = f"{value} GB"
            elif key == "storage_capacity_gb":
                value = f"{value} GB"
            elif key == "overall_rating":
                value = f"{value} ⭐"


            rows.append(f"| {field_name} | {value} |")

        if not rows:
            return "No specifications available."

        header = "| Specification | Value |\n|---------------|--------|"
        return header + "\n" + "\n".join(rows)

# Call LLM passing user_use_case and pc_data data in order for the LLM to generate a 
# summary of how it feels the pc fits the user's use case.  A prompt is included 
# below to tell the LLM how it should behave when interpretting the data. 
class ActionGenerateExplainFitPrompt(Action):

    def name(self) -> Text:
        return "action_generate_explain_fit_prompt"

    def run(self, dispatcher, tracker, domain):

        user_use_case = tracker.get_slot("user_use_case") or ""
        pc_data = tracker.get_slot("pc_data") or ""

        prompt = f"""
        You are a PC hardware expert.

        The user wants a PC for: {user_use_case}

        Here are the PC specifications:
        {pc_data}

        Briefly explain (in 3-4 sentences) whether this PC is a good fit.
        Mention any weaknesses.  
        Only mention weaknesses if they are objectively supported by the specifications.
        Do not mention the age of components unless obviously outdated.
        Don't dwell too much on high prices unless the 
        machine is unusually expensive or cheap as tech prices are fluctuating 
        quite a bit at the moment. 
        Keep the response under 100 words.
        """

        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        explanation = response.choices[0].message.content

        dispatcher.utter_message(text=explanation)

        return []

# Reset slots fields    
class ActionResetRecommendation(Action):
    def name(self) -> Text:
        return "action_reset_recommendation"

    def run(self, dispatcher, tracker, domain):

        return [
            SlotSet("user_device_type", None),
            SlotSet("user_use_case", None),
            SlotSet("user_budget", None),
            SlotSet("user_preferred_ram", None),
            SlotSet("user_needs_discrete_gpu", None),
            SlotSet("user_provide_detailed_specs", None),
            SlotSet("user_view_next_pc", None),
            SlotSet("user_start_again", None),
            SlotSet("pc_found", None),
            SlotSet("total_results", None),
            SlotSet("recommendation_index", None),
        ]

# Set the has_greeted slot to true
class ActionSetHasGreeted(Action):
    def name(self):
        return "action_set_has_greeted"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("has_greeted", True)]

