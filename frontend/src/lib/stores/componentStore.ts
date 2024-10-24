import AdminPage from '$lib/components/AdminPage.svelte';
import ChildrenGallery from '$lib/components/ChildrenGallery.svelte';
import ChildrenRegistration from '$lib/components/ChildrenRegistration.svelte';
import RadioList from '$lib/components/DataInput/RadioList.svelte';
import Milestone from '$lib/components/Milestone.svelte';
import MilestoneGroup from '$lib/components/MilestoneGroup.svelte';
import MilestoneOverview from '$lib/components/MilestoneOverview.svelte';
import ResearchPage from '$lib/components/ResearchPage.svelte';
import UserDataInput from '$lib/components/UserDataInput.svelte';

import { Fileupload, Input, MultiSelect, Select, Textarea } from 'flowbite-svelte';
import { writable } from 'svelte/store';

// put all the components here. can be an expanding list
export const componentTable = {
	userDataInput: UserDataInput,
	childrenGallery: ChildrenGallery,
	childrenRegistration: ChildrenRegistration,
	milestoneGroup: MilestoneGroup,
	milestoneOverview: MilestoneOverview,
	milestone: Milestone,
	radioList: RadioList,
	input: Input,
	multiSelect: MultiSelect,
	select: Select,
	fileupload: Fileupload,
	textarea: Textarea,
	adminPage: AdminPage,
	researchPage: ResearchPage
};
export const activeTabPersonal = writable('userDataInput');
export const activeTabChildren = writable('childrenGallery');
