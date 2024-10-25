import type { GetLanguagesResponse } from '$lib/client/types.gen';
import { type Writable, writable } from 'svelte/store';

export const lang_id = writable('de');

export const languages: Writable<GetLanguagesResponse> = writable({});
