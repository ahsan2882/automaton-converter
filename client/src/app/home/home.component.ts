import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import {
  UntypedFormControl,
  UntypedFormGroup,
  Validators,
} from '@angular/forms';

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

  fa_alphabetControl = new UntypedFormControl('', [Validators.required]);
  fa_statesControl = new UntypedFormControl('', [Validators.required]);
  fa_startState = new UntypedFormControl('', [Validators.required]);
  fa_acceptStates = new UntypedFormControl('', [Validators.required]);
  fa_transitionsControl = new UntypedFormControl('', [Validators.required]);

  finiteAutomatonFeatures = new UntypedFormGroup({
    alphabet: this.fa_alphabetControl,
    states: this.fa_statesControl,
    startState: this.fa_startState,
    acceptStates: this.fa_acceptStates,
    transitions: this.fa_transitionsControl,
  });
  showInvalidAlphabetError: boolean = false;
  invalidAlphabetError: string = 'Invalid alphabet defined in transitions';
  showInvalidStateError: boolean = false;
  invalidStateError: string = 'Invalid state defined in transitions';
  showInvalidStartStateLengthError: boolean = false;
  invalidStartStateLengthError: string = 'There can only be one start state';
  showInvalidStartStateError: boolean = false;
  invalidStartStateError: string = 'Invalid state defined as the start state';
  showInvalidAcceptStateError: boolean = false;
  invalidAcceptStateError: string = 'Invalid state defined as the start state';
  constructor(private httpClient: HttpClient) {}
  ngOnInit(): void {
    this.dropdownControl.valueChanges.subscribe((value: FA) => {
      this.selectedFA = value;
    });
    this.fa_acceptStates.valueChanges.subscribe((value: string) => {
      this.showInvalidAcceptStateError = false;
      this.fa_acceptStates.setErrors(null);
      const states: string[] = this.fa_statesControl.value.split(',');
      const acceptStates: string[] = value.split(',');
      acceptStates.forEach((state) => {
        if (!states.includes(state)) {
          this.showInvalidAcceptStateError = true;
          this.fa_acceptStates.setErrors({
            error: this.invalidAcceptStateError,
          });
        }
      });
    });
    this.fa_startState.valueChanges.subscribe((value: string) => {
      this.showInvalidStartStateError = false;
      this.showInvalidStartStateLengthError = false;
      this.fa_startState.setErrors(null);
      const states: string[] = this.fa_statesControl.value.split(',');
      if (value.includes(',')) {
        this.showInvalidStartStateLengthError = true;
        this.fa_startState.setErrors({
          error: this.invalidStartStateLengthError,
        });
      }
      if (!states.includes(value)) {
        this.showInvalidStartStateError = true;
        this.fa_startState.setErrors({ error: this.invalidStartStateError });
      }
    });
    this.fa_transitionsControl.valueChanges.subscribe((value: string) => {
      this.showInvalidAlphabetError = false;
      this.showInvalidStateError = false;
      this.fa_transitionsControl.setErrors(null);
      const alphabets: string[] = this.fa_alphabetControl.value.split(',');
      const states: string[] = this.fa_statesControl.value.split(',');
      const transitions = value.split('\n');
      transitions.forEach((transition) => {
        const [transit, next_state] = transition.split('->');
        const [state, symbol] = transit
          .replace('(', '')
          .replace(')', '')
          .split(',');
        if (symbol && !alphabets.includes(symbol)) {
          this.showInvalidAlphabetError = true;
          this.fa_transitionsControl.setErrors({
            error: this.invalidAlphabetError,
          });
        }
        if (
          (state?.length > 0 &&
            next_state?.length > 0 &&
            !states.includes(state)) ||
          !states.includes(next_state)
        ) {
          this.showInvalidStateError = true;
          this.fa_transitionsControl.setErrors({
            error: this.invalidStateError,
          });
        }
      });
    });
  }
  submitValues(): void {
    const transitions = this.getTransitions();
    const alphabets: string[] = this.fa_alphabetControl.value.split(',');
    const states: string[] = this.fa_statesControl.value.split(',');
    const startState: string = this.fa_startState.value;
    const acceptStates: string[] = this.fa_acceptStates.value.split(',');
    console.log({ alphabets, states, startState, acceptStates, transitions });
    this.httpClient
      .post(
        'http://127.0.0.1:5000/api/input_nfa',
        {
          alphabets,
          states,
          startState,
          acceptStates,
          transitions,
        },
        {
          headers: new HttpHeaders({
            'Content-Type': 'application/json',
          }),
        }
      )
      .subscribe(console.log);
  }

  private getTransitions(): Transition[] {
    const transitionArray: Transition[] = [];
    let transitionsObj: Transition;
    const transitions: string[] = this.fa_transitionsControl.value.split('\n');
    transitions.forEach((transition: string) => {
      const [transit, next_state] = transition.split('->');
      const [state, symbol] = transit
        .replace('(', '')
        .replace(')', '')
        .split(',');
      transitionsObj = { state, symbol, next_state };
      transitionArray.push(transitionsObj);
    });
    return transitionArray;
  }
}

interface Transition {
  state: string;
  symbol: string;
  next_state: string;
}
