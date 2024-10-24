import { writable, type Writable } from 'svelte/store';
import type { MilestoneGroupAdmin, UserQuestionAdmin } from '$lib/client/types.gen';

export const milestoneGroups: Writable<Record<string, Array<MilestoneGroupAdmin>>> = writable({});

export const userQuestions: Writable<Array<UserQuestionAdmin>> = writable([]);
