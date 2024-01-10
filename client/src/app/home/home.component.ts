import { Component, OnInit } from '@angular/core';
import { UntypedFormControl, UntypedFormGroup } from '@angular/forms';

enum FA {
  NFA = 'NFA',
  E_NFA = 'Epsilon-NFA',
  DFA = 'DFA',
  REGEXP = 'RegExp',
}

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements OnInit {
  automaton = FA;
  dropdownItems = [FA.NFA, FA.E_NFA, FA.DFA, FA.REGEXP];
  dropdownControl = new UntypedFormControl(this.dropdownItems[0]);
  selectedFA = this.dropdownItems[0];

  fa_alphabetControl = new UntypedFormControl('');
  fa_statesControl = new UntypedFormControl('');
  fa_startState = new UntypedFormControl('');
  fa_acceptStates = new UntypedFormControl('');
  fa_transitionsControl = new UntypedFormControl('');

  finiteAutomatonFeatures = new UntypedFormGroup({
    alphabet: this.fa_alphabetControl,
    states: this.fa_statesControl,
    startState: this.fa_startState,
    acceptStates: this.fa_acceptStates,
    transitions: this.fa_transitionsControl,
  });

  ngOnInit(): void {
    this.dropdownControl.valueChanges.subscribe((value: FA) => {
      this.selectedFA = value;
    });
  }
}
