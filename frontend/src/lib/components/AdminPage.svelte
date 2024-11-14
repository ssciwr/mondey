<svelte:options runes={true}/>

<script lang="ts">
import { adminUser, refreshMilestoneGroups } from "$lib/admin.svelte";
import Languages from "$lib/components/Admin/Languages.svelte";
import MilestoneExpectedAges from "$lib/components/Admin/MilestoneExpectedAges.svelte";
import MilestoneGroups from "$lib/components/Admin/MilestoneGroups.svelte";
import Questions from "$lib/components/Admin/Questions.svelte";
import Translations from "$lib/components/Admin/Translations.svelte";
import Users from "$lib/components/Admin/Users.svelte";
import { TabItem, Tabs } from "flowbite-svelte";
import {
	BadgeCheckOutline,
	ClipboardListOutline,
	LanguageOutline,
	ScaleBalancedOutline,
	UsersOutline,
} from "flowbite-svelte-icons";
import { onMount } from "svelte";
import { _ } from "svelte-i18n";

onMount(async () => {
	await adminUser.refresh();
	await refreshMilestoneGroups();
});
</script>

<Tabs tabStyle="underline" class="w-full">
    <TabItem open>
        <div slot="title" class="flex items-center gap-2">
            <BadgeCheckOutline size="md"/>
            {$_("admin.milestones")}
        </div>
        <MilestoneGroups/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <ScaleBalancedOutline size="md"/>
            {$_("admin.expected-age")}
        </div>
        <MilestoneExpectedAges/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <UsersOutline size="md"/>
            {$_("admin.users")}
        </div>
        <Users/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <ClipboardListOutline size="md"/>
            {$_("admin.user-questions")}
        </div>
        <Questions kind={"user"}/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <ClipboardListOutline size="md"/>
            {$_("admin.child-questions")}
        </div>
        <Questions kind={"child"}/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <LanguageOutline size="md"/>
            {$_("admin.translations")}
        </div>
        <Translations/>
    </TabItem>
    <TabItem>
        <div slot="title" class="flex items-center gap-2">
            <LanguageOutline size="md"/>
            {$_("admin.languages")}
        </div>
        <Languages/>
    </TabItem>
</Tabs>
