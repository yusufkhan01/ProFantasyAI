import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { SquadBuilderBanner } from '../SquadBuilderBanner'

describe('SquadBuilderBanner', () => {
  it('renders the title and flags the feature as coming soon', () => {
    render(<SquadBuilderBanner />)
    expect(screen.getByRole('heading', { name: 'Build your FPL Squad' })).toBeInTheDocument()
    // "Coming soon" appears as both the status pill and the disabled CTA.
    expect(screen.getAllByText('Coming soon')).toHaveLength(2)
  })

  it('disables the call-to-action while the feature is unreleased', () => {
    render(<SquadBuilderBanner />)
    expect(screen.getByRole('button', { name: 'Coming soon' })).toBeDisabled()
  })
})
