<script>
import {
	Footer,
	FooterBrand,
	FooterIcon,
	FooterLink,
	FooterLinkGroup,
} from "flowbite-svelte";
import { FacebookSolid, InstagramSolid } from "flowbite-svelte-icons";
import { _ } from "svelte-i18n";
</script>

  <Footer footerType="socialmedia" class="bg-zinc-700">
    <div class="flex justify-between items-center px-1">
      <div class="mb-2 mr-5 lg:ml-11 md:ml-10 max-sm:mr-3 max-sm:ml-1">
        <FooterBrand class="flex" href="/" src="/src/lib/assets/mondey_dark.svg" alt="MONDEY logo"/>
      </div>
      <div class="grid grid-cols-2 gap-9 sm:grid-cols-2 min-md:mr-20 lg:mr-20 ml-3">
        <div>
          <h2 class="mb-6 mt-4 text-sm font-semibold text-white uppercase dark:text-white">{$_("footer.information")}</h2>
          <FooterLinkGroup>
            <FooterLink liClass="mb-2 text-sm max-sm:text-xs text-zinc-400" href="/">{$_("footer.research")}</FooterLink>
            <FooterLink liClass="mb-2 text-sm max-sm:text-xs text-zinc-400" href="/">{$_("footer.imprint")}</FooterLink>
            <FooterLink liClass="mb-2 text-sm max-sm:text-xs text-zinc-400" href="/">{$_("footer.privacy")}</FooterLink>
          </FooterLinkGroup>
        </div>
        <div>
          <h2 class="mb-6 mt-4 text-sm font-semibold uppercase text-white dark:text-white">{$_("footer.contact")}</h2>
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
        <span class="block text-xs text-zinc-400 sm:text-center dark:text-gray-400">© 2024 <!--[--><a href="/" class="hover:underline">{$_("footer.bottom")}</a><!--]-->
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
