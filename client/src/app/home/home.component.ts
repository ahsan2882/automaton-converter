import { Component, OnInit } from '@angular/core';
import { UntypedFormBuilder, UntypedFormControl, FormGroup } from '@angular/forms';

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
  constructor(private formBuilder: UntypedFormBuilder) {}

  ngOnInit(): void {
    this.dropdownControl.valueChanges.subscribe((value: FA) => {
      // Do something with the selected value
      this.selectedFA = value;
      console.log('Selected value:', value);
    });
  }
}
