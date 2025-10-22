from django import forms
import re

class NumbersForm(forms.Form):
    numbers = forms.CharField(
        widget=forms.Textarea(attrs={"rows":4, "cols":40}),
        label="Enter 10–15 numbers (separate by comma, space, newline or semicolon)",
        help_text="Example: 12.3, 4, 5.6 7 8"
    )

    def clean_numbers(self):
        raw = self.cleaned_data["numbers"].strip()
        # split on whitespace, commas, or semicolons
        tokens = re.split(r'[\s,;]+', raw)
        nums = []
        for t in tokens:
            if t == "":
                continue
            try:
                nums.append(float(t))
            except ValueError:
                raise forms.ValidationError(f"Invalid number: {t}")
        if not (10 <= len(nums) <= 15):
            raise forms.ValidationError("Please enter between 10 and 15 numbers.")
        return nums
