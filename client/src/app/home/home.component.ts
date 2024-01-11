import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import {
  UntypedFormControl,
  UntypedFormGroup,
  Validators,
} from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

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

  equivalentNFA_image: SafeResourceUrl = '';
  equivalentDFA_image: SafeResourceUrl = '';
  equivalent_eNFA_image: SafeResourceUrl = '';
  equivalentRegexp: string = '';

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
  constructor(
    private httpClient: HttpClient,
    private _sanitizer: DomSanitizer
  ) {}
  ngOnInit(): void {
    this.dropdownControl.valueChanges.subscribe((value: FA) => {
      this.selectedFA = value;
      this.fa_alphabetControl.setValue('');
      this.fa_statesControl.setValue('');
      this.fa_startState.setValue('');
      this.fa_acceptStates.setValue('');
      this.fa_transitionsControl.setValue('');
      this.equivalentDFA_image = '';
      this.equivalentNFA_image = '';
      this.equivalentRegexp = '';
      this.equivalent_eNFA_image = '';
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
      .post<NFA_Response>(
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
            'Access-Control-Allow-Origin': '*',
          }),
        }
      )
      .subscribe((response: NFA_Response) => {
        // let response: NFA_Response = {
        //   result_regexp: '(ab+ba)*',
        //   result_dfa:
        //     'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+DQo8IURPQ1RZUEUgc3ZnIFBVQkxJQyAiLS8vVzNDLy9EVEQgU1ZHIDEuMS8vRU4iDQogImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+DQo8IS0tIEdlbmVyYXRlZCBieSBncmFwaHZpeiB2ZXJzaW9uIDkuMC4wICgyMDIzMDkxMS4xODI3KQ0KIC0tPg0KPHN2ZyB3aWR0aD0iMjI1cHQiIGhlaWdodD0iMTExcHQiDQogdmlld0JveD0iMC4wMCAwLjAwIDIyMy43NiAxNTAuODgiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPg0KPGcgaWQ9ImdyYXBoMCIgY2xhc3M9ImdyYXBoIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSg0IDEwNi44OCkiPg0KPHRpdGxlPk5GQTwvdGl0bGU+DQo8cG9seWdvbiBmaWxsPSJ3aGl0ZSIgc3Ryb2tlPSJub25lIiBwb2ludHM9Ii00LDQgLTQsLTEwNi44OCAyMTkuNzYsLTEwNi44OCAyMTkuNzYsNCAtNCw0Ii8+DQo8IS0tIHEwIC0tPg0KPGcgaWQ9ImVkZ2UwIiBmaWxsPSJibGFjayI+DQogICAgICAgIDxwb2x5Z29uIHBvaW50cz0iDQogICAgICAgICAgMCwtNTAgLTUsLTQ1IC01LC01NSIvPg0KICAgICAgICA8cmVjdCB4PSItMzAiIHk9Ii01MSIgd2lkdGg9IjI3IiBoZWlnaHQ9IjIiLz4NCiAgICA8L2c+DQo8ZyBpZD0ibm9kZTEiIGNsYXNzPSJub2RlIj4NCjx0aXRsZT5xMDwvdGl0bGU+DQo8ZWxsaXBzZSBmaWxsPSJub25lIiBzdHJva2U9ImJsYWNrIiBjeD0iMjQuMTMiIGN5PSItNDkuMTMiIHJ4PSIyMC4xMyIgcnk9IjIwLjEzIi8+DQo8ZWxsaXBzZSBmaWxsPSJub25lIiBzdHJva2U9ImJsYWNrIiBjeD0iMjQuMTMiIGN5PSItNDkuMTMiIHJ4PSIyNC4xMyIgcnk9IjI0LjEzIi8+DQo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIyNC4xMyIgeT0iLTQzLjciIGZvbnQtZmFtaWx5PSJUaW1lcyBOZXcgUm9tYW4sc2VyaWYiIGZvbnQtc2l6ZT0iMTQuMDAiPnEwPC90ZXh0Pg0KPC9nPg0KPCEtLSBxMSAtLT4NCjxnIGlkPSJub2RlMiIgY2xhc3M9Im5vZGUiPg0KPHRpdGxlPnExPC90aXRsZT4NCjxlbGxpcHNlIGZpbGw9Im5vbmUiIHN0cm9rZT0iYmxhY2siIGN4PSIxMTEuODgiIGN5PSItNzguMTMiIHJ4PSIyMC4xMyIgcnk9IjIwLjEzIi8+DQo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxMTEuODgiIHk9Ii03Mi43IiBmb250LWZhbWlseT0iVGltZXMgTmV3IFJvbWFuLHNlcmlmIiBmb250LXNpemU9IjE0LjAwIj5xMTwvdGV4dD4NCjwvZz4NCjwhLS0gcTAmIzQ1OyZndDtxMSAtLT4NCjxnIGlkPSJlZGdlMSIgY2xhc3M9ImVkZ2UiPg0KPHRpdGxlPnEwJiM0NTsmZ3Q7cTE8L3RpdGxlPg0KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSJibGFjayIgZD0iTTM5Ljk5LC02Ny40MkM0Ny4wOCwtNzQuNzEgNTYuMjEsLTgyLjI3IDY2LjI1LC04Ni4xMyA3MS4xOCwtODguMDIgNzYuNTksLTg4LjM3IDgxLjg5LC04Ny44NiIvPg0KPHBvbHlnb24gZmlsbD0iYmxhY2siIHN0cm9rZT0iYmxhY2siIHBvaW50cz0iODIuNDgsLTkxLjMxIDkxLjYsLTg1LjkyIDgxLjExLC04NC40NCA4Mi40OCwtOTEuMzEiLz4NCjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjcwIiB5PSItODkuNTgiIGZvbnQtZmFtaWx5PSJUaW1lcyBOZXcgUm9tYW4sc2VyaWYiIGZvbnQtc2l6ZT0iMTQuMDAiPmE8L3RleHQ+DQo8L2c+DQo8IS0tIHEyIC0tPg0KPGcgaWQ9Im5vZGUzIiBjbGFzcz0ibm9kZSI+DQo8dGl0bGU+cTI8L3RpdGxlPg0KPGVsbGlwc2UgZmlsbD0ibm9uZSIgc3Ryb2tlPSJibGFjayIgY3g9IjExMS44OCIgY3k9Ii0yMC4xMyIgcng9IjIwLjEzIiByeT0iMjAuMTMiLz4NCjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjExMS44OCIgeT0iLTE0LjciIGZvbnQtZmFtaWx5PSJUaW1lcyBOZXcgUm9tYW4sc2VyaWYiIGZvbnQtc2l6ZT0iMTQuMDAiPnEyPC90ZXh0Pg0KPC9nPg0KPCEtLSBxMCYjNDU7Jmd0O3EyIC0tPg0KPGcgaWQ9ImVkZ2UyIiBjbGFzcz0iZWRnZSI+DQo8dGl0bGU+cTAmIzQ1OyZndDtxMjwvdGl0bGU+DQo8cGF0aCBmaWxsPSJub25lIiBzdHJva2U9ImJsYWNrIiBkPSJNNDYuMjIsLTM5LjI1QzUyLjU3LC0zNi40OSA1OS42MiwtMzMuNjMgNjYuMjUsLTMxLjM4IDcwLjkzLC0yOS43OSA3NS45NiwtMjguMzEgODAuODksLTI2Ljk4Ii8+DQo8cG9seWdvbiBmaWxsPSJibGFjayIgc3Ryb2tlPSJibGFjayIgcG9pbnRzPSI4MS43LC0zMC4zOSA5MC41NCwtMjQuNTQgNzkuOTksLTIzLjYgODEuNywtMzAuMzkiLz4NCjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjcwIiB5PSItMzMuNTgiIGZvbnQtZmFtaWx5PSJUaW1lcyBOZXcgUm9tYW4sc2VyaWYiIGZvbnQtc2l6ZT0iMTQuMDAiPmI8L3RleHQ+DQo8L2c+DQo8IS0tIHExJiM0NTsmZ3Q7cTAgLS0+DQo8ZyBpZD0iZWRnZTQiIGNsYXNzPSJlZGdlIj4NCjx0aXRsZT5xMSYjNDU7Jmd0O3EwPC90aXRsZT4NCjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iYmxhY2siIGQ9Ik05Mi4zNSwtNzEuODZDODIuMzEsLTY4LjQ2IDY5LjYsLTY0LjE3IDU3Ljk0LC02MC4yMiIvPg0KPHBvbHlnb24gZmlsbD0iYmxhY2siIHN0cm9rZT0iYmxhY2siIHBvaW50cz0iNTkuMjQsLTU2Ljk3IDQ4LjY0LC01Ny4wOCA1Ni45OSwtNjMuNiA1OS4yNCwtNTYuOTciLz4NCjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjcwIiB5PSItNjcuNTgiIGZvbnQtZmFtaWx5PSJUaW1lcyBOZXcgUm9tYW4sc2VyaWYiIGZvbnQtc2l6ZT0iMTQuMDAiPmI8L3RleHQ+DQo8L2c+DQo8IS0tIHEzIC0tPg0KPGcgaWQ9Im5vZGU0IiBjbGFzcz0ibm9kZSI+DQo8dGl0bGU+cTM8L3RpdGxlPg0KPGVsbGlwc2UgZmlsbD0ibm9uZSIgc3Ryb2tlPSJibGFjayIgY3g9IjE5NS42MyIgY3k9Ii00OC4xMyIgcng9IjIwLjEzIiByeT0iMjAuMTMiLz4NCjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjE5NS42MyIgeT0iLTQyLjciIGZvbnQtZmFtaWx5PSJUaW1lcyBOZXcgUm9tYW4sc2VyaWYiIGZvbnQtc2l6ZT0iMTQuMDAiPnEzPC90ZXh0Pg0KPC9nPg0KPCEtLSBxMSYjNDU7Jmd0O3EzIC0tPg0KPGcgaWQ9ImVkZ2UzIiBjbGFzcz0iZWRnZSI+DQo8dGl0bGU+cTEmIzQ1OyZndDtxMzwvdGl0bGU+DQo8cGF0aCBmaWxsPSJub25lIiBzdHJva2U9ImJsYWNrIiBkPSJNMTMxLjAyLC03MS40N0MxNDEuMjIsLTY3LjczIDE1NC4xOCwtNjIuOTcgMTY1Ljc0LC01OC43MyIvPg0KPHBvbHlnb24gZmlsbD0iYmxhY2siIHN0cm9rZT0iYmxhY2siIHBvaW50cz0iMTY2LjY1LC02Mi4xMiAxNzQuODMsLTU1LjM5IDE2NC4yNCwtNTUuNTUgMTY2LjY1LC02Mi4xMiIvPg0KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTUzLjc1IiB5PSItNjUuNTgiIGZvbnQtZmFtaWx5PSJUaW1lcyBOZXcgUm9tYW4sc2VyaWYiIGZvbnQtc2l6ZT0iMTQuMDAiPmE8L3RleHQ+DQo8L2c+DQo8IS0tIHEyJiM0NTsmZ3Q7cTAgLS0+DQo8ZyBpZD0iZWRnZTUiIGNsYXNzPSJlZGdlIj4NCjx0aXRsZT5xMiYjNDU7Jmd0O3EwPC90aXRsZT4NCjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iYmxhY2siIGQ9Ik05NCwtMTAuNkM4NS41LC03LjA3IDc1LjE0LC00LjcyIDY2LjI1LC04LjM4IDU5LjAxLC0xMS4zNiA1Mi4zNiwtMTYuMyA0Ni42MiwtMjEuNzMiLz4NCjxwb2x5Z29uIGZpbGw9ImJsYWNrIiBzdHJva2U9ImJsYWNrIiBwb2ludHM9IjQ0LjI4LC0xOS4xMSAzOS45NCwtMjguNzggNDkuMzYsLTIzLjkzIDQ0LjI4LC0xOS4xMSIvPg0KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNzAiIHk9Ii0xMS41OCIgZm9udC1mYW1pbHk9IlRpbWVzIE5ldyBSb21hbixzZXJpZiIgZm9udC1zaXplPSIxNC4wMCI+YTwvdGV4dD4NCjwvZz4NCjwhLS0gcTImIzQ1OyZndDtxMyAtLT4NCjxnIGlkPSJlZGdlNiIgY2xhc3M9ImVkZ2UiPg0KPHRpdGxlPnEyJiM0NTsmZ3Q7cTM8L3RpdGxlPg0KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSJibGFjayIgZD0iTTEzMS4xMiwtMjYuMzVDMTM5LjIsLTI5LjExIDE0OC44MywtMzIuNCAxNTcuNSwtMzUuMzggMTYwLjA2LC0zNi4yNSAxNjIuNzIsLTM3LjE2IDE2NS4zOCwtMzguMDgiLz4NCjxwb2x5Z29uIGZpbGw9ImJsYWNrIiBzdHJva2U9ImJsYWNrIiBwb2ludHM9IjE2NC4xLC00MS4zNCAxNzQuNjksLTQxLjI3IDE2Ni4zNywtMzQuNzIgMTY0LjEsLTQxLjM0Ii8+DQo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxNTMuNzUiIHk9Ii0zNy41OCIgZm9udC1mYW1pbHk9IlRpbWVzIE5ldyBSb21hbixzZXJpZiIgZm9udC1zaXplPSIxNC4wMCI+YjwvdGV4dD4NCjwvZz4NCjwhLS0gcTMmIzQ1OyZndDtxMyAtLT4NCjxnIGlkPSJlZGdlNyIgY2xhc3M9ImVkZ2UiPg0KPHRpdGxlPnEzJiM0NTsmZ3Q7cTM8L3RpdGxlPg0KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSJibGFjayIgZD0iTTE4OC4xLC02Ni45NkMxODYuODIsLTc3LjA1IDE4OS4zMywtODYuMjUgMTk1LjYzLC04Ni4yNSAxOTkuMzcsLTg2LjI1IDIwMS43NywtODMuMDEgMjAyLjg0LC03OC4yNiIvPg0KPHBvbHlnb24gZmlsbD0iYmxhY2siIHN0cm9rZT0iYmxhY2siIHBvaW50cz0iMjA2LjMzLC03OC41NyAyMDMuMTIsLTY4LjQ3IDE5OS4zNCwtNzguMzcgMjA2LjMzLC03OC41NyIvPg0KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTk1LjYzIiB5PSItODguNyIgZm9udC1mYW1pbHk9IlRpbWVzIE5ldyBSb21hbixzZXJpZiIgZm9udC1zaXplPSIxNC4wMCI+YSxiPC90ZXh0Pg0KPC9nPg0KPC9nPg0KPC9zdmc+DQo=',
        // };
        console.log(response);
        if (response?.result_nfa) {
          this.equivalentNFA_image =
            this._sanitizer.bypassSecurityTrustResourceUrl(
              'data:image/svg+xml;base64,' + response.result_nfa
            );
        }
        this.equivalentDFA_image =
          this._sanitizer.bypassSecurityTrustResourceUrl(
            'data:image/svg+xml;base64,' + response.result_dfa
          );
        this.equivalentRegexp = response.result_regexp;
      });
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

interface NFA_Response {
  result_enfa?: string;
  result_nfa?: string;
  result_dfa: string;
  result_regexp: string;
}

interface Transition {
  state: string;
  symbol: string;
  next_state: string;
}
