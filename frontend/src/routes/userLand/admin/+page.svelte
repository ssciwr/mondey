<svelte:options runes={true}/>

<script lang="ts">
import AdminDocuments from "$lib/components/Admin/AdminDocuments.svelte";
import AnswerSessionData from "$lib/components/Admin/AnswerSessionData.svelte";
import CalendarEvents from "$lib/components/Admin/CalendarEvents.svelte";
import DeactivateFeedback from "$lib/components/Admin/DeactivateFeedback.svelte";
import Languages from "$lib/components/Admin/Languages.svelte";
import MilestoneExpectedAges from "$lib/components/Admin/MilestoneExpectedAges.svelte";
import MilestoneGroups from "$lib/components/Admin/MilestoneGroups.svelte";
import Questions from "$lib/components/Admin/Questions.svelte";
import Translations from "$lib/components/Admin/Translations.svelte";
import Users from "$lib/components/Admin/Users.svelte";
import { i18n } from "$lib/i18n.svelte";
import { milestoneGroups } from "$lib/stores/adminStore.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import { TabItem, Tabs } from "flowbite-svelte";
import {
	BadgeCheckOutline,
	CalendarMonthSolid,
	ClipboardListOutline,
	DatabaseOutline,
	FileOutline,
	LanguageOutline,
	PersonChalkboardOutline,
	ScaleBalancedOutline,
	UsersOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";

onMount(async () => {
	try {
		await user.load();
		await milestoneGroups.refresh();
	} catch (error) {
		alertStore.showAlert(
			error instanceof Error ? error.message : String(error),
			"",
			true,
			true,
		);
	}
});
</script>

<Tabs tabStyle="underline">
    <TabItem open>
        {#snippet titleSlot()}
        <div class="flex items-center gap-2">
            <BadgeCheckOutline size="md"/>
            {i18n.tr.admin.milestones}
        </div>
        {/snippet}
        <MilestoneGroups/>
    </TabItem>
    <TabItem>
        {#snippet titleSlot()}
        <div class="flex items-center gap-2">
            <ScaleBalancedOutline size="md"/>
            {i18n.tr.admin.expectedAge}
        </div>
        {/snippet}
        <MilestoneExpectedAges/>
    </TabItem>
    <TabItem>
        {#snippet titleSlot()}
        <div class="flex items-center gap-2">
            <FileOutline size="md" />
            {i18n.tr.admin.adminDocuments}
        </div>
        {/snippet}
        <AdminDocuments/>
    </TabItem>
    <TabItem>
        {#snippet titleSlot()}
        <div class="flex items-center gap-2">
            <UsersOutline size="md"/>
            {i18n.tr.admin.users}
        </div>
        {/snippet}
        <Users/>
    </TabItem>
    <TabItem>
        {#snippet titleSlot()}
        <div class="flex items-center gap-2">
            <CalendarMonthSolid class="shrink-0 h-6 w-6"/>
            {i18n.tr.admin.calendarEvents}
        </div>
        {/snippet}
        <CalendarEvents/>
    </TabItem>
    <TabItem>
        {#snippet titleSlot()}
        <div class="flex items-center gap-2">
            <ClipboardListOutline size="md"/>
            {i18n.tr.admin.userQuestions}
        </div>
        {/snippet}
        <Questions kind={"user"}/>
    </TabItem>
    <TabItem>
        {#snippet titleSlot()}
        <div class="flex items-center gap-2">
            <ClipboardListOutline size="md"/>
            {i18n.tr.admin.childQuestions}
        </div>
        {/snippet}
        <Questions kind={"child"}/>
    </TabItem>
    <TabItem>
        {#snippet titleSlot()}
        <div class="flex items-center gap-2">
            <DatabaseOutline size="md"/>
            {i18n.tr.admin.data}
        </div>
        {/snippet}
        <AnswerSessionData />
    </TabItem>
    <TabItem>
        {#snippet titleSlot()}
        <div class="flex items-center gap-2">
            <LanguageOutline size="md"/>
            {i18n.tr.admin.translations}
        </div>
        {/snippet}
        <Translations/>
    </TabItem>
    <TabItem>
        {#snippet titleSlot()}
        <div class="flex items-center gap-2">
            <LanguageOutline size="md"/>
            {i18n.tr.admin.languages}
        </div>
        {/snippet}
        <Languages/>
    </TabItem>
    <TabItem>
        {#snippet titleSlot()}
        <div class="flex items-center gap-2">
            <PersonChalkboardOutline size="md"/>
            {i18n.tr.admin.feedbackConfiguration}
        </div>
        {/snippet}
        <DeactivateFeedback/>
    </TabItem>
</Tabs>
