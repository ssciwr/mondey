<svelte:options runes={true}/>

<script lang="ts">
import { refreshMilestoneGroups } from "$lib/admin.svelte";
import Languages from "$lib/components/Admin/Languages.svelte";
import MilestoneExpectedAges from "$lib/components/Admin/MilestoneExpectedAges.svelte";
import MilestoneGroups from "$lib/components/Admin/MilestoneGroups.svelte";
import Questions from "$lib/components/Admin/Questions.svelte";
import SubmittedMilestoneImages from "$lib/components/Admin/SubmittedMilestoneImages.svelte";
import Translations from "$lib/components/Admin/Translations.svelte";
import Users from "$lib/components/Admin/Users.svelte";
import { i18n } from "$lib/i18n.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { TabItem, Tabs } from "flowbite-svelte";
import {
	BadgeCheckOutline,
	ClipboardListOutline,
	FileImageOutline,
	LanguageOutline,
	ScaleBalancedOutline,
	UsersOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";

onMount(async () => {
	try {
		await user.load();
		await refreshMilestoneGroups();
	} catch (error) {
		alertStore.showAlert(error.message, "", true, true);
	}
});
</script>

<Tabs tabStyle="underline" class="w-full">
    <TabItem open>
        <div slot="title" class="flex items-center gap-2">
            <BadgeCheckOutline size="md"/>
            {i18n.tr.admin.milestones}
        </div>
        <MilestoneGroups/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <ScaleBalancedOutline size="md"/>
            {i18n.tr.admin.expectedAge}
        </div>
        <MilestoneExpectedAges/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <FileImageOutline size="md"/>
            {i18n.tr.admin.submittedImages}
        </div>
        <SubmittedMilestoneImages/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <UsersOutline size="md"/>
            {i18n.tr.admin.users}
        </div>
        <Users/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <ClipboardListOutline size="md"/>
            {i18n.tr.admin.userQuestions}
        </div>
        <Questions kind={"user"}/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <ClipboardListOutline size="md"/>
            {i18n.tr.admin.childQuestions}
        </div>
        <Questions kind={"child"}/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <LanguageOutline size="md"/>
            {i18n.tr.admin.translations}
        </div>
        <Translations/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <LanguageOutline size="md"/>
            {i18n.tr.admin.languages}
        </div>
        <Languages/>
    </TabItem>
</Tabs>
