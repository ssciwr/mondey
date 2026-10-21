<script lang="ts">
import {
	AdjustmentsVerticalOutline,
	ArrowRightToBracketOutline,
	AtomOutline,
	CogSolid,
	GridPlusSolid,
	LanguageOutline,
	ProfileCardSolid,
	SunOutline,
} from "flowbite-svelte-icons";
import { i18n } from "#lib/i18n.svelte.ts";

import { goto } from "$app/navigation";
import { Sidebar, SidebarGroup, SidebarItem, Tooltip } from "flowbite-svelte";
import DarkModeChooser from "#lib/components/DarkModeChooser.svelte";
import LocaleSidebarDropdown from "#lib/components/LocaleSidebarDropdown.svelte";
import { alertStore } from "#lib/stores/alertStore.svelte.ts";
import { currentChild } from "#lib/stores/childrenStore.svelte.ts";
import { user } from "#lib/stores/userStore.svelte.ts";

let { setHideDrawer }: { setHideDrawer: (to: boolean) => void } = $props();
</script>

<Sidebar disableBreakpoints position="static">
        <SidebarGroup class="space-y-2 mt-10">
            <SidebarItem label  = {user.data?.email ?
              (user.data.email.length > 20 ?
                user.data.email.substring(0, 20) + "..." :
                user.data.email) :
              ""}  spanClass="ms-3 font-bold"/><Tooltip title={user.data?.email} placement="top">{user.data?.email}</Tooltip>
            <SidebarItem label = {i18n.tr.userData.label} href="/userLand/dataInput">
                {#snippet icon()}
                    <ProfileCardSolid size="lg" />
                {/snippet}
            </SidebarItem>

            <SidebarItem label = {i18n.tr.childData.overviewLabel} href="/userLand/children">
                {#snippet icon()}
                    <GridPlusSolid size="lg" />
                {/snippet}
            </SidebarItem>

            {#if user.data?.is_superuser}
                <SidebarItem label = {i18n.tr.admin.label} href="/userLand/admin">
                    {#snippet icon()}
                        <CogSolid size="lg" />
                    {/snippet}
                </SidebarItem>
            {/if}

            {#if user.data?.is_researcher}
                <SidebarItem label = {i18n.tr.researcher.label} href="/userLand/research">
                    {#snippet icon()}
                        <AtomOutline size="lg" />
                    {/snippet}
                </SidebarItem>
            {/if}

        </SidebarGroup>
        <SidebarGroup border borderClass="space-y-2 pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
            <SidebarItem label = {i18n.tr.userData.settingsLabel} href="/userLand/settings">
                {#snippet icon()}
                    <AdjustmentsVerticalOutline size="lg" />
                {/snippet}
            </SidebarItem>
            <SidebarItem>
                {#snippet icon()}
                    <SunOutline />
                {/snippet}
                {#snippet subtext()}
                    <DarkModeChooser />
                {/snippet}
            </SidebarItem>


            <SidebarItem label = {i18n.tr.login.profileButtonLabelLogout} aClass="cursor-pointer" onclick = {async () => {
                    const response = await user.logout();
                    if (response.error) {
                       alertStore.showAlert(
                        i18n.tr.login.alertMessageTitle,
                        "",
                        true,
                        true
                    );
                    } else {
                        user.data = null;
                        currentChild.id = null;
                        currentChild.data = null;
                        setHideDrawer(true)
                        goto(`/`);
                    }
                }}>
                {#snippet icon()}
                    <ArrowRightToBracketOutline size="lg" />
                {/snippet}
            </SidebarItem>
            <LocaleSidebarDropdown />
        </SidebarGroup>
</Sidebar>
