import { type Writable, writable } from 'svelte/store';
import type { GetLanguagesResponse } from '$lib/client/types.gen';

export const lang_id = writable('1');

export const languages: Writable<GetLanguagesResponse> = writable({});
