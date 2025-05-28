<svelte:options runes={true} />

<script lang="ts">
import logo_dark from "$lib/assets/mondey_dark.svg";
import { i18n } from "$lib/i18n.svelte";
import {
	Footer,
	FooterBrand,
	FooterIcon,
	FooterLink,
	FooterLinkGroup,
} from "flowbite-svelte";
import { FacebookSolid, InstagramSolid } from "flowbite-svelte-icons";
</script>



  <Footer footerType="socialmedia" class="bg-zinc-700">
    <div class="w-full text-center min-w-full">
      <a href="/">
        <img class="h-16 sm:block lg:hidden inline" src={logo_dark} alt="MONDEY logo"/>
      </a>
    </div>
    <div class="flex justify-between items-center px-1">
      <div class="mb-2 mr-5 lg:ml-11 md:ml-10 max-sm:mr-3 max-sm:ml-1">
        <FooterBrand imgClass="me-3 h-16 hidden lg:block" class="flex" href="/" src={logo_dark} alt="MONDEY logo"/>
      </div>
      <div class="grid grid-cols-2 gap-9 sm:grid-cols-2 min-md:mr-20 lg:mr-20 ml-3">
        <div>
          <h2 class="mb-6 mt-4 text-sm font-semibold text-white uppercase dark:text-white">{i18n.tr.footer.information}</h2>
          <FooterLinkGroup>
            <FooterLink liClass="mb-2 text-sm max-sm:text-xs text-zinc-400" href="/">{i18n.tr.footer.research}</FooterLink>
            <FooterLink liClass="mb-2 text-sm max-sm:text-xs text-zinc-400" href="/">{i18n.tr.footer.imprint}</FooterLink>
            <FooterLink liClass="mb-2 text-sm max-sm:text-xs text-zinc-400" href="/">{i18n.tr.footer.privacy}</FooterLink>
          </FooterLinkGroup>
        </div>
        <div>
          <h2 class="mb-6 mt-4 text-sm font-semibold uppercase text-white dark:text-white">{i18n.tr.footer.contact}</h2>
          <FooterLinkGroup>
            <FooterLink liClass="mb-2 text-sm max-sm:text-xs text-zinc-400" href="/">+49 6221 547346</FooterLink>
            <FooterLink liClass="mb-2 text-sm max-sm:text-xs text-zinc-400" href="/">Hauptstraße 47-51, 69117 Heidelberg</FooterLink>
            <FooterLink liClass="mb-2 text-sm max-sm:text-xs text-zinc-400 break-words" href="/">E-Mail: support@psychologie.uni-heidelberg.de</FooterLink>
          </FooterLinkGroup>
        </div>
      </div>
    </div>
    <hr class="my-6 border-gray-200 sm:mx-auto dark:border-gray-700 lg:my-8" />
    <div class="sm:flex sm:items-center sm:justify-between">
      <div class="flex mt-4 space-x-6 rtl:space-x-reverse sm:mt-0">
        <span class="block text-xs text-zinc-400 sm:text-center dark:text-gray-400">
          © 2025 <a href="/" class="hover:underline">{i18n.tr.footer.bottom}</a>
        </span>
        <span class="block text-xs text-zinc-400 sm:text-center dark:text-gray-400">
          <a href="https://github.com/ssciwr/mondey" class="hover:underline">{i18n.tr.footer.website}</a> {i18n.tr.footer.developedByThe} <a href="https://ssc.uni-heidelberg.de" class="hover:underline">Scientific Software Center, Heidelberg University</a>
        </span>
        <FooterIcon href="/">
          <FacebookSolid class="w-5 h-5 text-white dark:text-zinc-500 hover:text-gray-900 dark:hover:text-white" />
        </FooterIcon>
        <FooterIcon href="/">
          <InstagramSolid class="w-5 h-5 text-white dark:text-zinc-500 hover:text-gray-900 dark:hover:text-white" />
        </FooterIcon>
      </div>
    </div>
  </Footer>
