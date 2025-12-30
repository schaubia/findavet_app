# Bulgarian Translation Guide for Sofia Vet Platform

## Translation System Overview

The app now has a **bilingual system** with English and Bulgarian support! 

### How It Works

1. **Translation Dictionary** - All text is stored in the `TRANSLATIONS` dictionary at the top of `streamlit_app.py`
2. **Translation Function** - Use `t('key', lang)` to get translated text
3. **Language Selector** - Two buttons in the sidebar: 🇬🇧 English | 🇧🇬 Български

## Current Status

✅ **Completed:**
- Translation dictionary with 80+ keys
- Language selector in sidebar
- Main navigation translated
- Page titles translated  
- Search location section translated

⚠️ **Partially Complete:**
The translation system is set up, but not all UI elements are using it yet. You need to replace hardcoded English text with translation function calls.

## How to Complete the Translation

### Pattern to Follow:

**Before:**
```python
st.button("Search")
st.markdown("**Services**")
st.write(f"Found {count} clinics")
```

**After:**
```python
st.button(t('search_btn', lang))
st.markdown(f"**{t('services', lang)}**")
st.write(t('found_clinics', lang, count=count))
```

### Where to Add Translations:

Search through `streamlit_app.py` and replace:

1. **All st.button() text**
   - "Search" → `t('search_btn', lang)`
   - "Clear" → `t('clear_btn', lang)`
   - "Register Clinic" → `t('register_btn', lang)`

2. **All st.header() / st.subheader() text**
   - "Search Filters" → `t('search_filters', lang)`
   - "Services Offered" → `t('services_offered_label', lang)`

3. **All st.text_input() labels and placeholders**
   - "Clinic Name*" → `t('clinic_name', lang)`
   - placeholder="..." → `placeholder=t('clinic_name_placeholder', lang)`

4. **All st.checkbox() labels**
   - "Emergency Care" → `t('emergency_care', lang)`

5. **All st.write() / st.markdown() text**
   - "Address:" → `f"**{t('address', lang)}:**"`

6. **All st.success() / st.error() / st.warning() messages**
   - "Clinic registered successfully!" → `t('clinic_registered', lang, name=name)`

7. **All form labels, help text, and column headers**

## Translation Keys Already Available

Check the `TRANSLATIONS` dictionary (lines 17-258) for all available keys:

- Page titles: `app_title`, `app_subtitle`, `navigation`
- Search: `search_header`, `search_filters`, `search_btn`, etc.
- Clinic details: `contact_info`, `address`, `phone`, `email`, etc.
- Forms: `clinic_name`, `register_btn`, `fill_required`, etc.
- Messages: `clinic_registered`, `review_submitted`, `no_clinics_found`

## Adding New Translation Keys

If you need a new translation key:

```python
TRANSLATIONS = {
    'en': {
        # ... existing keys ...
        'your_new_key': 'English text here',
    },
    'bg': {
        # ... existing keys ...
        'your_new_key': 'Български текст тук',
    }
}
```

## Testing

1. Run the app
2. Click 🇬🇧 English button → check all English text
3. Click 🇧🇬 Български button → check all Bulgarian text
4. Make sure all buttons, labels, and messages switch languages

## Quick Find & Replace Guide

### Service Names (Keep in English in Database)
The service names in the database ("Cat Hotel", "Dog Hotel", etc.) should remain in English for consistency. Only the UI labels should be translated.

### Emojis
Keep all emojis - they're universal! 🐱🏥💉🔬

### Numbers and Formatting
These work the same in both languages:
- Ratings: ⭐ 4.5
- Distances: 2.5 km
- Coordinates: 42.6977, 23.3219

## Example: Fully Translated Section

```python
if page == t('add_clinic', lang):
    st.header(f"🏥 {t('register_clinic', lang)}")
    
    with st.form("add_clinic_form"):
        st.subheader(t('basic_info', lang))
        name = st.text_input(
            t('clinic_name', lang),
            placeholder=t('clinic_name_placeholder', lang)
        )
        address = st.text_input(
            t('address', lang),
            placeholder=t('address_placeholder', lang)
        )
        
        submitted = st.form_submit_button(
            f"✅ {t('register_btn', lang)}",
            use_container_width=True
        )
        
        if submitted:
            if name and address:
                st.success(t('clinic_registered', lang, name=name))
            else:
                st.error(t('fill_required', lang))
```

## Tips

1. **Always pass `lang` parameter**: `t('key', lang)`
2. **Use f-strings for formatting**: `f"{t('text', lang)} {variable}"`
3. **Use .format() for variables in translations**: `t('found_clinics', lang, count=5)`
4. **Keep key names descriptive**: `clinic_name` not `cn`
5. **Group related keys**: All form fields together, all messages together

## Priority Areas

Focus on translating these high-impact areas first:

1. ✅ Language selector (Done)
2. ✅ Main navigation (Done)
3. ✅ Page titles (Done)
4. ⏳ Search filters and buttons
5. ⏳ Clinic registration form
6. ⏳ Success/error messages
7. ⏳ Clinic details display
8. ⏳ About section in sidebar

## Need Help?

All the translation keys are in the dictionary (lines 17-258). Just search for the English text you want to translate, find its key, and use `t('key', lang)`.

Example:
- Want to translate "Search"? 
- Find it in TRANSLATIONS: `'search_btn': 'Search'`
- Use: `t('search_btn', lang)`
- Result in Bulgarian: "Търси"

Good luck! 🚀
