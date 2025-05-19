<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
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

import { goto } from "$app/navigation";
import DarkModeChooser from "$lib/components/DarkModeChooser.svelte";
import LocaleChooser from "$lib/components/LocaleChooser.svelte";
import { alertStore } from "$lib/stores/alertStore.svelte";
import { currentChild } from "$lib/stores/childrenStore.svelte";
import { user } from "$lib/stores/userStore.svelte";
import {
	Sidebar,
	SidebarGroup,
	SidebarItem,
	SidebarWrapper,
	Tooltip,
} from "flowbite-svelte";

let { setHideDrawer } = $props();
</script>

<Sidebar>
    <SidebarWrapper>
        <SidebarGroup class="mt-10">
            <SidebarItem label  = {user.data?.email ?
              (user.data.email.length > 20 ?
                user.data.email.substring(0, 20) + "..." :
                user.data.email) :
              ""}  class = "font-bold"/><Tooltip title={user.data?.email} placement="top">{user.data?.email}</Tooltip>
            <SidebarItem label = {i18n.tr.userData.label} href="/userLand/dataInput">
                <svelte:fragment slot="icon">
                    <ProfileCardSolid size="lg" />
                </svelte:fragment>
            </SidebarItem>

            <SidebarItem label = {i18n.tr.childData.overviewLabel} href="/userLand/children">
                <svelte:fragment slot="icon">
                    <GridPlusSolid size="lg" />
                </svelte:fragment>
            </SidebarItem>

            {#if user.data?.is_superuser}
                <SidebarItem label = {i18n.tr.admin.label} href="/userLand/admin">
                    <svelte:fragment slot="icon">
                        <CogSolid size="lg" />
                    </svelte:fragment>
                </SidebarItem>
            {/if}

            {#if user.data?.is_researcher}
                <SidebarItem label = {i18n.tr.researcher.label} href="/userLand/research">
                    <svelte:fragment slot="icon">
                        <AtomOutline size="lg" />
                    </svelte:fragment>
                </SidebarItem>
            {/if}

        </SidebarGroup>
        <SidebarGroup border>
            <SidebarItem label = {i18n.tr.userData.settingsLabel} href="/userLand/settings">
                <svelte:fragment slot="icon">
                    <AdjustmentsVerticalOutline size="lg" />
                </svelte:fragment>
            </SidebarItem>
            <SidebarItem>
                <svelte:fragment slot="icon">
                    <SunOutline />
                </svelte:fragment>
                <svelte:fragment slot="subtext">
                    <DarkModeChooser />
                </svelte:fragment>
            </SidebarItem>


            <SidebarItem label = {i18n.tr.login.profileButtonLabelLogout} onclick = {async () => {
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
                <svelte:fragment slot="icon">
                    <ArrowRightToBracketOutline size="lg" />
                </svelte:fragment>
            </SidebarItem>
            <SidebarItem>
                <svelte:fragment slot="icon">
                    <LanguageOutline size="lg" />
                </svelte:fragment>
                <svelte:fragment slot="subtext">
                    <LocaleChooser />
                </svelte:fragment>
            </SidebarItem>
        </SidebarGroup>
    </SidebarWrapper>
</Sidebar>
