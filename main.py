import PySimpleGUI as sg
import json
from datetime import datetime
from collections import defaultdict
import os

class PokemonDeckTracker:
    def __init__(self):
        self.matches = []
        self.decks = set()
        self.archetypes = set()
        self.last_used_deck = None
        
    def add_match(self, my_deck, opponent_archetype, won, notes=""):
        match = {
            'id': self._get_next_id(),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'deck': my_deck,
            'opponent': opponent_archetype,
            'result': 'draw' if won is None else ('win' if won else 'loss'),
            'notes': notes
        }
        self.matches.append(match)
        self.decks.add(my_deck)
        self.archetypes.add(opponent_archetype)
        self.last_used_deck = my_deck
        return match['id']
    
    def _get_next_id(self):
        """Get next available ID for a match"""
        if not self.matches:
            return 0
        return max(match.get('id', 0) for match in self.matches) + 1
        
    def _ensure_match_ids(self):
        """Ensure all matches have an ID"""
        next_id = 0
        for match in self.matches:
            if 'id' not in match:
                match['id'] = next_id
                next_id += 1
            else:
                next_id = max(next_id, match['id'] + 1)
    
    def edit_match(self, match_id, my_deck, opponent_archetype, won, notes=""):
        for match in self.matches:
            if match.get('id') == match_id:
                old_deck = match['deck']
                old_opponent = match['opponent']
                
                match['deck'] = my_deck
                match['opponent'] = opponent_archetype
                match['result'] = 'win' if won else 'loss'
                match['notes'] = notes
                
                self._update_collections()
                return True
        return False
    
    def delete_match(self, match_id):
        self.matches = [m for m in self.matches if m.get('id') != match_id]
        self._update_collections()
    
    def _update_collections(self):
        """Update decks and archetypes sets based on current matches"""
        self.decks = set(match['deck'] for match in self.matches)
        self.archetypes = set(match['opponent'] for match in self.matches)
    
    def get_match_by_id(self, match_id):
        for match in self.matches:
            if match.get('id') == match_id:
                return match
        return None
    
    def get_all_matches(self):
        return sorted(self.matches, key=lambda x: x['date'], reverse=True)
    
    def get_deck_stats(self, deck_name=None):
        stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'matchups': defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0})})
        
        for match in self.matches:
            if deck_name and match['deck'] != deck_name:
                continue
                
            deck = match['deck']
            opponent = match['opponent']
            result = match['result']
            
            if result == 'win':
                stats[deck]['wins'] += 1
                stats[deck]['matchups'][opponent]['wins'] += 1
            elif result == 'loss':
                stats[deck]['losses'] += 1
                stats[deck]['matchups'][opponent]['losses'] += 1
            else:  
                stats[deck]['draws'] += 1
                stats[deck]['matchups'][opponent]['draws'] += 1
        
        return stats
    
    def get_stats_text(self, deck_name=None):
        stats = self.get_deck_stats(deck_name)
        text = ""
        
        for deck in stats:
            total_matches = stats[deck]['wins'] + stats[deck]['losses'] + stats[deck]['draws']
            winrate = (stats[deck]['wins'] / total_matches * 100) if total_matches > 0 else 0
            
            text += f"\n=== Stats for deck: {deck} ===\n"
            text += f"Overall record: {stats[deck]['wins']}-{stats[deck]['draws']}-{stats[deck]['losses']} ({winrate:.1f}%)\n\n"
            text += "Matchups:\n"
            
            for opponent, results in stats[deck]['matchups'].items():
                matchup_matches = results['wins'] + results['losses'] + results['draws']
                matchup_winrate = (results['wins'] / matchup_matches * 100) if matchup_matches > 0 else 0
                text += f"- vs {opponent}: {results['wins']}-{results['draws']}-{results['losses']} ({matchup_winrate:.1f}%)\n"
        
        return text
        
    def rename_deck(self, old_name, new_name):
        """Přejmenuje balíček a aktualizuje všechny související záznamy"""
        if new_name in self.decks:
            return False, "Deck with this name already exists"
        if old_name not in self.decks:
            return False, "Original deck not found"
        for match in self.matches:
            if match['deck'] == old_name:
                match['deck'] = new_name
        self.decks.remove(old_name)
        self.decks.add(new_name)
        return True, "Deck renamed successfully"
    
    def delete_deck(self, deck_name):
        """Smaže balíček a všechny jeho zápasy"""
        if deck_name not in self.decks:
            return False, "Deck not found"
        self.matches = [m for m in self.matches if m['deck'] != deck_name]
        self._update_collections()
        return True, "Deck and its matches deleted successfully"
    
    def save_to_file(self, filename):
        self._ensure_match_ids()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'matches': self.matches,
                'decks': list(self.decks),
                'archetypes': list(self.archetypes)
            }, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.matches = data['matches']
                self.decks = set(data['decks'])
                self.archetypes = set(data['archetypes'])
                self._ensure_match_ids()
            return True
        except FileNotFoundError:
            return False

def create_selection_window(title, options):
    layout = [
        [sg.Text(f'Select {title}:', font=('Helvetica', 10))],
        [sg.Listbox(values=sorted(options), size=(30, 6), key='-SELECTION-', font=('Helvetica', 10))],
        [sg.Button('Select', size=(10, 1)), sg.Button('Cancel', size=(10, 1))]
    ]
    window = sg.Window(f'Select {title}', layout, modal=True, font=('Helvetica', 10))
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            window.close()
            return None
        if event == 'Select':
            selection = values['-SELECTION-'][0] if values['-SELECTION-'] else None
            window.close()
            return selection

def create_matches_window(tracker):
    matches = tracker.get_all_matches()
    
    headers = ['Date', 'Deck', 'Opponent', 'Result', 'Notes']
    data = [[m['date'], m['deck'], m['opponent'], m['result'], m['notes']] for m in matches]
    
    layout = [
        [sg.Table(values=data,
                 headings=headers,
                 auto_size_columns=True,
                 justification='left',
                 num_rows=min(25, len(data)),
                 key='-TABLE-',
                 enable_events=True,
                 font=('Helvetica', 10))],
        [sg.Button('Edit', size=(10, 1)), sg.Button('Delete', size=(10, 1)), 
         sg.Button('Close', size=(10, 1))]
    ]
    
    return sg.Window('Match History', layout, modal=True, finalize=True, font=('Helvetica', 10))

def create_edit_match_window(match):
    layout = [
        [sg.Text("Your Deck:", size=(12, 1)), sg.Input(key='-DECK-', size=(20, 1)), 
        sg.Button("Select Deck", size=(10, 1))],
        [sg.Text("Opp. Archetype:", size=(12, 1)), sg.Input(key='-ARCHETYPE-', size=(20, 1)), 
        sg.Button("Select Archetype", size=(10, 1))],
        [sg.Text("Notes:", size=(12, 1)), sg.Input(key='-NOTES-', size=(20, 1)), 
        sg.Button("Show Stats", size=(10, 1))],
        [sg.Text("Result:", size=(12, 1))],
        [sg.Radio("Win", "RESULT", key='-WIN-', default=True),
        sg.Radio("Loss", "RESULT", key='-LOSS-'),
        sg.Radio("Draw", "RESULT", key='-DRAW-')],
        [sg.Button("Submit"), sg.Button("Exit")]
    ]
    
    return sg.Window('Edit Match', layout, modal=True, finalize=True, font=('Helvetica', 10))

def create_deck_management_window(tracker):
    decks = sorted(list(tracker.decks))
    
    layout = [
        [sg.Text('Manage Decks', font=('Helvetica', 16), pad=(0, 10))],
        [sg.Column([
            [sg.Listbox(values=decks,
                       size=(30, 10),
                       key='-DECK_LIST-',
                       enable_events=True,
                       font=('Helvetica', 10))],
            [sg.Column([
                [sg.Button('Rename', size=(12, 1)), sg.Button('Delete', size=(12, 1))],
                [sg.Button('Close', size=(12, 1))]
            ], justification='center')]
        ], justification='center', pad=(10, 10))]
    ]
    
    return sg.Window('Deck Management', 
                    layout, 
                    modal=True, 
                    finalize=True,
                    font=('Helvetica', 10))

def create_rename_deck_window(old_name):
    layout = [
        [sg.Text('Rename Deck', font=('Helvetica', 14), pad=(0, 10))],
        [sg.Text('Current name:', size=(12, 1)), sg.Text(old_name, font=('Helvetica', 10, 'bold'))],
        [sg.Text('New name:', size=(12, 1)), sg.Input(key='-NEW_NAME-', size=(25, 1))],
        [sg.Button('Save', size=(10, 1)), sg.Button('Cancel', size=(10, 1))]
    ]
    
    return sg.Window('Rename Deck', 
                    layout, 
                    modal=True, 
                    finalize=True,
                    font=('Helvetica', 10))

def create_main_window():
    sg.theme('LightGrey1')
    button_size = (12, 1)
    input_size = (20, 1)
    label_size = (15, 1)
    section_padding = (0, 15)
    
    header_layout = [
        [sg.Column(
            [[sg.Image('static/logo.png', subsample=1)]], 
            justification='center', 
            expand_x=True
        )]
    ]
    
    match_details_layout = [
        [sg.Text('Your Deck:', size=label_size), 
         sg.Input(key='-DECK-', size=input_size), 
         sg.Button('Select Deck', size=button_size)],
        [sg.Text('Opponent Archetype:', size=label_size), 
         sg.Input(key='-OPPONENT-', size=input_size), 
         sg.Button('Select Archetype', size=button_size)],
        [sg.Text('Result:', size=label_size), 
         sg.Radio('Win', 'RESULT', key='-WIN-', default=True), 
         sg.Radio('Draw', 'RESULT', key='-DRAW-'),
         sg.Radio('Loss', 'RESULT', key='-LOSS-')],
        [sg.Text('Notes:', size=label_size), 
         sg.Input(key='-NOTES-', size=(35, 1))],
        [sg.Button('Add Match', size=button_size)]
    ]

    stats_layout = [
        [sg.Text('Select Deck:', size=label_size), 
         sg.Combo(['All Decks'], key='-STAT_DECK-', size=(18,1)), 
         sg.Button('Show Stats', size=button_size)],
        [sg.Multiline(size=(45, 10), key='-STATS-', disabled=True, font=('Courier', 10))]
    ]

    layout = [
        header_layout,
        [sg.Frame('Match Details', match_details_layout, font=('Helvetica', 10), pad=section_padding)],
        [sg.Frame('View Stats', stats_layout, font=('Helvetica', 10), pad=section_padding)],
        [sg.Column([
            [sg.Button('Edit Decks', size=(12, 1)),
             sg.Button('View Match History', size=(15, 1)), 
             sg.Button('Exit', size=(10, 1))]
        ], justification='right', pad=section_padding)]
    ]

    return sg.Window('Pokemon Pocket Deck Tracker', 
                     layout, 
                     finalize=True, 
                     font=('Helvetica', 10),
                     resizable=True)

def main():
    tracker = PokemonDeckTracker()
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    filename = os.path.join(data_dir, 'pokemon_stats.json')
    
    if not tracker.load_from_file(filename):
        sg.popup('Welcome to Pokemon Pocket Deck Tracker!\nNo existing data found, starting fresh.')
    
    main_window = create_main_window()
    
    while True:
        event, values = main_window.read()
        
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
            
        elif event == 'Select Deck':
            deck_list = sorted(list(tracker.decks))
            if deck_list:
                choice = create_selection_window('Deck', deck_list)
                if choice:
                    main_window['-DECK-'].update(choice)
            else:
                sg.popup('No decks found. Add your first match to create a deck!')
                
        elif event == 'Select Archetype':
            archetype_list = sorted(list(tracker.archetypes))
            if archetype_list:
                choice = create_selection_window('Archetype', archetype_list)
                if choice:
                    main_window['-OPPONENT-'].update(choice)
            else:
                sg.popup('No archetypes found. Add your first match to create an archetype!')
                
        elif event == 'Add Match':
            deck = values['-DECK-'].strip()
            opponent = values['-OPPONENT-'].strip()
            
            if not deck or not opponent:
                sg.popup_error('Please enter both deck and opponent archetype!')
                continue
                
            won = values['-WIN-']
            draw = values['-DRAW-']
            notes = values['-NOTES-'].strip()
            result = None if draw else won
            
            tracker.add_match(deck, opponent, result, notes)
            tracker.save_to_file(filename) 
            main_window['-STAT_DECK-'].update(values=['All Decks'] + sorted(list(tracker.decks)))
            main_window['-STAT_DECK-'].update(deck)  
            stats_text = tracker.get_stats_text(deck)
            main_window['-STATS-'].update(stats_text)
            
            main_window['-DECK-'].update('')
            main_window['-OPPONENT-'].update('')
            main_window['-NOTES-'].update('')
            sg.popup('Match added successfully!')
            
        elif event == 'Show Stats':
            selected_deck = values['-STAT_DECK-']
            if selected_deck == 'All Decks':
                selected_deck = None
            stats_text = tracker.get_stats_text(selected_deck)
            main_window['-STATS-'].update(stats_text)
            
        elif event == 'Edit Decks':
            deck_window = create_deck_management_window(tracker)
            
            while True:
                deck_event, deck_values = deck_window.read()
                
                if deck_event in (sg.WIN_CLOSED, 'Close'):
                    break
                    
                elif deck_event == 'Rename':
                    if not deck_values['-DECK_LIST-']:
                        sg.popup_error('Please select a deck to rename')
                        continue
                        
                    old_name = deck_values['-DECK_LIST-'][0]
                    rename_window = create_rename_deck_window(old_name)
                    
                    while True:
                        rename_event, rename_values = rename_window.read()
                        
                        if rename_event in (sg.WIN_CLOSED, 'Cancel'):
                            break
                            
                        elif rename_event == 'Save':
                            new_name = rename_values['-NEW_NAME-'].strip()
                            if not new_name:
                                sg.popup_error('Please enter a new name')
                                continue
                                
                            success, message = tracker.rename_deck(old_name, new_name)
                            if success:
                                tracker.save_to_file(filename) 
                                sg.popup('Deck renamed successfully!')
                                deck_window['-DECK_LIST-'].update(values=sorted(list(tracker.decks)))
                                main_window['-STAT_DECK-'].update(values=['All Decks'] + sorted(list(tracker.decks)))
                                break
                            else:
                                sg.popup_error(message)
                                
                    rename_window.close()
                    
                elif deck_event == 'Delete':
                    if not deck_values['-DECK_LIST-']:
                        sg.popup_error('Please select a deck to delete')
                        continue
                        
                    deck_name = deck_values['-DECK_LIST-'][0]
                    if sg.popup_yes_no(f'Are you sure you want to delete deck "{deck_name}" and all its matches?', 
                                     title='Confirm Deletion') == 'Yes':
                        success, message = tracker.delete_deck(deck_name)
                        if success:
                            tracker.save_to_file(filename)  
                            sg.popup(message)
                            deck_window['-DECK_LIST-'].update(values=sorted(list(tracker.decks)))
                            main_window['-STAT_DECK-'].update(values=['All Decks'] + sorted(list(tracker.decks)))
                        else:
                            sg.popup_error(message)
            
            deck_window.close()
            
        elif event == 'View Match History':
            matches_window = create_matches_window(tracker)
            while True:
                matches_event, matches_values = matches_window.read()
                
                if matches_event in (sg.WIN_CLOSED, 'Close'):
                    break
                    
                elif matches_event == 'Edit':
                    if len(matches_values['-TABLE-']) == 0:
                        sg.popup('Please select a match to edit')
                        continue
                        
                    selected_row = matches_values['-TABLE-'][0]
                    match_id = tracker.get_all_matches()[selected_row]['id']
                    match = tracker.get_match_by_id(match_id)
                    
                    if match:
                        edit_window = create_edit_match_window(match)
                        while True:
                            edit_event, edit_values = edit_window.read()
                            
                            if edit_event in (sg.WIN_CLOSED, 'Cancel'):
                                break
                                
                            elif edit_event == 'Save Changes':
                                tracker.edit_match(
                                    match_id,
                                    edit_values['-DECK-'].strip(),
                                    edit_values['-OPPONENT-'].strip(),
                                    edit_values['-WIN-'],
                                    edit_values['-NOTES-'].strip()
                                )
                                tracker.save_to_file(filename)
                                tracker.last_used_deck = edit_values['-DECK-'].strip()

                                main_window['-STAT_DECK-'].update(values=['All Decks'] + sorted(list(tracker.decks)))
                                main_window['-STAT_DECK-'].update(tracker.last_used_deck)
                                main_window['-STATS-'].update(tracker.get_stats_text(tracker.last_used_deck))

                                sg.popup('Match updated successfully!')
                                break
                                
                        edit_window.close()
                        matches_window.close()
                        matches_window = create_matches_window(tracker)
                        
                elif matches_event == 'Delete':
                    if len(matches_values['-TABLE-']) == 0:
                        sg.popup('Please select a match to delete')
                        continue
                        
                    if sg.popup_yes_no('Are you sure you want to delete this match?') == 'Yes':
                        selected_row = matches_values['-TABLE-'][0]
                        match_id = tracker.get_all_matches()[selected_row]['id']
                        tracker.delete_match(match_id)
                        tracker.save_to_file(filename)
                        sg.popup('Match deleted successfully!')
                        main_window['-STAT_DECK-'].update(values=['All Decks'] + sorted(list(tracker.decks)))
                        if tracker.last_used_deck in tracker.decks:
                            main_window['-STAT_DECK-'].update(tracker.last_used_deck)
                            main_window['-STATS-'].update(tracker.get_stats_text(tracker.last_used_deck))
                        else:
                            main_window['-STAT_DECK-'].update('All Decks')
                            main_window['-STATS-'].update(tracker.get_stats_text(None))
                        matches_window.close()
                        matches_window = create_matches_window(tracker)
            
            matches_window.close()
            main_window['-STAT_DECK-'].update(values=['All Decks'] + sorted(list(tracker.decks)))
    
    main_window.close()

if __name__ == '__main__':
    main()
